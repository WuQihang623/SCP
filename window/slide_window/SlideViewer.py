import os
import sys
import cv2
import json
import pickle
import constants
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QPoint, Qt, QEvent, pyqtSignal, QPointF, QSize
from PyQt5.QtGui import QWheelEvent, QMouseEvent,  QPixmap, QColor, QPen
from window.slide_window.BasicSlideViewer import BasicSlideViewer
from window.Tools import ToolManager
from window.TileLoader.PatchLineLoader import PatchLineLoader
from window.TileLoader.NucleusMarkLoader import NucleusMarkLoader
from window.TileLoader.RegionContourLoader import RegionContourLoader
from window.TileLoader.NucleiContourLoader import NucleiContourLoader

class SlideViewer(BasicSlideViewer):
    """
        SlideViewer类的功能是，显示标注，显示细胞核，轮廓等结果
    """
    # 发送激活标注的索引信号
    reactivateItemSignal = pyqtSignal(int, float)

    def __init__(self, mainViewerFlag=True):
        super(SlideViewer, self).__init__()
        # 主窗口标识
        self.mainViewerFlag = mainViewerFlag
        # 初始化标注工具
        self.ToolManager = ToolManager(self.view, self.scene)

        # 组织区域轮廓加载器
        self.RegionContourLoader = RegionContourLoader(scene=self.scene)
        self.RegionContourLoader.addContourItemSignal.connect(self.addContourItem)
        self.RegionContourLoader.removeItemSignal.connect(self.removeContourItem)
        self.PatchLineLoader = PatchLineLoader(self.scene)
        self.PatchLineLoader.addLineItemSignal.connect(self.addContourItem)
        self.PatchLineLoader.removeLineItemSignal.connect(self.removeContourItem)
        # 细胞核轮廓加载器
        self.NucleiContourLoader = NucleiContourLoader(scene=self.scene)
        self.NucleusMarkLoader = NucleusMarkLoader(scene=self.scene)

    def initVariable(self):
        super(SlideViewer, self).initVariable()
        self.heatmap_dict = None
        self.heatmap_properties = None
        self.showItemHeatmap = None

        self.nucleus_contour = None
        self.nucleus_type = None
        self.nucleus_center = None
        self.nucleus_properties = None
        self.nucleus_color_dict = None
        self.showItemNucleus = set([])

        self.tissue_contours = None
        self.tissue_type = None
        self.tissue_properties = None
        self.tissue_color_dict = None
        self.showItemTissueContour = set([])

        self.nucleus_diff_properties = None
        self.nucleus_diff = None
        self.nucleus_diff_color_dict = None
        self.showItemNucleusDiff = set([])

        self.modify_nucleus_flag = False


    # 载入slide
    def loadSlide(self, slide_path, zoom_step=1.25):
        super(SlideViewer, self).loadSlide(slide_path, zoom_step)
        # 设置测量工具的mpp
        self.ToolManager.measure_tool.set_mpp(self.slide_helper.mpp)

        # TODO: 信号连接
        # self.load_nuclues_action.triggered.connect(self.choose_pkl_file)
        # self.change_heatmap_alpha_action.triggered.connect(self.change_heatmap_alpha)

    def eventFilter(self, qobj: 'QObject', event: 'QEvent') -> bool:
        # 如果不是鼠标事件或者滚轮事件，则不进行事件的传递
        event_porcessed = False
        # 鼠标事件
        if isinstance(event, QMouseEvent):
            event_porcessed = self.processMouseEvent(event)
        elif isinstance(event, QWheelEvent):
            event_porcessed = self.processWheelEvent(event)
        return event_porcessed

    def processMouseEvent(self, event: QMouseEvent):
        """
            鼠标事件
        """
        if self.slide_helper is None:
            return True
        # 获取当前的一个level以及下采样倍数
        # downsample = self.slide_helper.get_downsample_for_level(self.current_level)
        # 鼠标左键
        if event.button() == Qt.LeftButton:
            if event.type() == QEvent.MouseButtonPress:
                # 设置鼠标拖动视图标志
                self.move_flag = True
                self.start_mouse_pos_x = event.pos().x()
                self.start_mouse_pos_y = event.pos().y()
                # 标注的绘制
                self.ToolManager.mousePressEvent(event, self.current_downsample)

            elif event.type() == QEvent.MouseButtonRelease:
                self.move_flag = False
                # 标注的绘制
                self.ToolManager.mouseReleaseEvent(event, self.current_downsample)

            elif event.type() == QEvent.MouseButtonDblClick:
                reply = False
                if hasattr(self, 'ToolManager'):
                    if self.ToolManager.TOOL_FLAG == 1:
                        # TODO: 允许修改细胞核结果
                        reply = self.modify_nucleus(event.pos())
                if hasattr(self, "ToolManager"):
                    if reply is False:
                        self.ToolManager.mouseDoubleClickEvent(event, self.current_downsample)

        elif event.button() == Qt.RightButton:
            # 鼠标右键
            if event.type() == QEvent.MouseButtonRelease:
                self.menu.exec_(self.mapToGlobal(event.pos()))

        elif event.type() == QEvent.MouseMove:
            # 更新状态栏鼠标位置
            self.mousePosSignal.emit(self.view.mapToScene(event.pos()))
            # 视图移动
            if (self.move_flag and self.moveAllowFlag):
                self.responseMouseMove(event)
            else:
                self.ToolManager.mouseMoveEvent(event, self.current_downsample)
            # 同步图像的鼠标绘制
            if self.Registration:
                pos = self.view.mapToScene(event.pos())
                self.pairMouseSignal.emit(pos)
        return True

    def responseMouseMove(self, event):
        """
            鼠标拖动页面
        """
        super().responseMouseMove(event)
        # 绘制细胞核分割结果
        self.show_nuclei()

    def responseWheelEvent(self, mousePos: QPoint, zoom):
        """
            鼠标滚轮操作
        """
        super().responseWheelEvent(mousePos, zoom)
        # 显示细胞核轮廓
        self.show_nuclei()

    def update_scale_view(self, level, scene_view_rect, clear_scene_flag, mouse_pos):
        # 更新图像视图
        super(SlideViewer, self).update_scale_view(level, scene_view_rect, clear_scene_flag, mouse_pos)
        if clear_scene_flag:
            downsample = self.slide_helper.get_downsample_for_level(level)
            # 重新绘制标注
            self.ToolManager.redraw(level, downsample)

            # 重新绘制区域分割结果
            self.show_contour()
            self.show_line()

    def loadAllAnnotation(self):
        """
            导入标注时重新绘制所有的标注
        """
        self.ToolManager.redraw(self.current_level, self.current_downsample)

    def switch2annotation(self, pos, choosed_idx):
        """ 点击标注，跳转到当前level下以pos为中心的画面下
        :param pos: 标注的中心
        :param choosed_idx: 被选中的标注的索引
        :return:
        """
        # downsample = self.slide_helper.get_downsample_for_level(self.current_level)
        x1 = pos[0] / self.current_downsample
        x2 = pos[2] / self.current_downsample
        y1 = pos[1] / self.current_downsample
        y2 = pos[3] / self.current_downsample
        pos = QPoint((x1 + x2) / 2, (y1 + y2) / 2)
        self.switch2pos(pos)
        # 发送信号，通知ToolManager可以删除上一个激活的item并重画，再重画当前激活的item
        self.reactivateItemSignal.emit(choosed_idx, self.current_downsample)
        # 如果有同步窗口，跳转到同步窗口的相应位置
        if self.Registration:
            self.moveTogetherSignal.emit([pos.x() * self.current_downsample, pos.y() * self.current_downsample])

    def switch2pos(self, pos):
        """
            跳转到当前level下的以pos为中心的区域
        """
        super().switch2pos(pos)
        # 绘制细胞核分割结果
        self.show_nuclei()

    def showImageAtThumbnailArea(self, pos, thumbnail_dimension):
        """
            点击缩略图，跳转到对应区域
        """
        super(SlideViewer, self).showImageAtThumbnailArea(pos, thumbnail_dimension)


    def show_annotation_slot(self, *args):
        """
            显示标注
        """
        self.ToolManager.redraw(self.current_level, self.current_downsample)

    def load_nucleus_slot(self, properties, nucleus_info):
        """
            载入细胞核分割结果
            Args:
                properties: {
                    "肿瘤细胞": {"type": 1, "color": [255, 0, 0], "number": 1000},
                    "淋巴细胞": {"type": 2, "color": [0, 255, 0], "number": 1000},
                    "中性粒细胞": {"type": 3, "color": [255, 255, 0], "number": 1000},
                    "基质细胞": {"type": 4, "color": [0, 0, 255], "number": 1000},
                },
                nucleus_info:{
                    "type": ndarray,
                    "center": ndarray,
                    "contour": ndarray,
                }
        """
        self.nucleus_properties = properties
        self.nucleus_type = nucleus_info["type"]
        self.nucleus_center = nucleus_info["center"]
        self.nucleus_contour = nucleus_info["contour"]
        self.nucleus_color_dict = {}
        for name, item in properties.items():
            self.nucleus_color_dict[item["type"]] = item["color"]

    def load_heatmap_slot(self, properties, heatmap_info):
        """
            Args:
                properties: {
                    "heatmap": ["组织区域热力图", "边界区域热力图"],
                    "downsample": int,
                },
                heatmap_info: {
                    "组织区域热力图": ndarray,
                    "边界区域热力图": ndarray,
                }
        """
        self.heatmap_properties = properties
        self.heatmap_dict = heatmap_info

    def load_contour_slot(self, properties, contour_info):
        """
            Args:
                properties: {
                    "肿瘤区域": {"color": [255, 0, 0], "type": 1},
                    "基质区域": {"color": [0, 255, 0], "type": 2},
                    "图像块": {"color": [0, 0, 0], "type": 3}
                }
                contour_info: {
                    "contour": ndarray,  array[array(contour1), array(contour2), ...]
                    "type": ndarray, array[1, 2, 3, ...]
                }
        """
        self.tissue_properties = properties
        self.tissue_contours = contour_info["contour"]
        self.tissue_type = contour_info["type"]
        self.tissue_color_dict = {}
        for name, item in properties.items():
            self.tissue_color_dict[item["type"]] = item["color"]

    def load_nucleus_diff_slot(self, properties, nucleus_diff_info):
        """
            Args:
                properties: {
                    "FN": {"color": [255, 0, 0]},
                    "FP": {"color": [0, 255, 0]},
                }
                nucleus_diff_info: {
                    "center": ndarray,
                    "diff_array": ndarray = ["TP", "TN", "FP", "FN", ...]
                }
        """
        if self.nucleus_center is not None:
            if nucleus_diff_info["diff_array"].shape[0] != self.nucleus_center.shape[0]:
                return
        else:
            self.nucleus_center = nucleus_diff_info["center"]
        self.nucleus_diff = nucleus_diff_info["diff_array"]
        self.nucleus_diff_properties = properties
        self.nucleus_diff_color_dict = {}
        for name, item in properties.items():
            self.nucleus_diff_color_dict[name] = item["color"]

    def show_nucleus_slot(self, showItem: list, clear_nuclues=False):
        """
            显示细胞核分割结果
            Args:
                showItem: 是一个列表，存放了要显示的细胞核类型 ["肿瘤细胞", "淋巴细胞", ...]
        """
        if self.nucleus_contour is None or self.nucleus_center is None or self.nucleus_type is None:
            return
        showType = []
        for type_name in showItem:
            showType.append(self.nucleus_properties.get(type_name, {}).get("type", -1))
        showType = set(showType)
        # TODO:
        showType_copy = showType.copy()
        # showType = showType - self.showItemNucleus
        removeType = self.showItemNucleus - showType
        self.showItemNucleus = showType_copy

        # TODO: last_nuclei?
        if clear_nuclues:
            self.NucleiContourLoader.last_nuclei = None
        self.NucleiContourLoader.load_contour(current_rect=self.get_current_view_scene_rect(),
                                              current_level=self.current_level,
                                              current_downsample=self.current_downsample,
                                              contours=self.nucleus_contour,
                                              centers=self.nucleus_center,
                                              types=self.nucleus_type,
                                              color_dict=self.nucleus_color_dict,
                                              show_types=list(showType) if len(showType) != 0 else None,
                                              remove_types=list(removeType) if len(removeType) != 0 else None)

    def show_heatmap_slot(self, showItem: list):
        """
            Args:
                showItem: 是一个列表，存放了要显示的热力图类型 ["组织区域热力图"] or []
        """
        if self.heatmap_dict is None or self.heatmap_properties is None:
            return
        if self.showItemHeatmap == showItem:
            return
        if len(showItem) != 0:
            self.heatmap = self.heatmap_dict[showItem[0]]
            self.heatmap_downsample = self.heatmap_properties["downsample"]
            self.TileLoader.update_heatmap_background(self.heatmap, self.heatmap_alpha, self.heatmap_downsample)
            self.reshowView(self.heatmap, self.heatmap_downsample)
        else:
            self.heatmap = None
            self.heatmap_downsample = None
            self.reshowView(self.heatmap, self.heatmap_downsample)

    def show_contour_slot(self, showItem, update_level=False):
        """
            Args:
                showItem: 是一个列表，存放了要显示的轮廓["肿瘤区域"， "基质区域", ...] or []
        """
        if self.tissue_contours is None or self.tissue_properties is None or self.tissue_type is None:
            return
        showType = []
        for type_name in showItem:
            showType.append(self.tissue_properties.get(type_name, {}).get("type", -1))
        showType = set(showType)
        if update_level == False:
            removeType = self.showItemTissueContour - showType
        else:
            removeType = []
        self.showItemTissueContour = showType

        self.RegionContourLoader.load_contour(current_level=self.current_level,
                                              current_downsample=self.current_downsample,
                                              contours=self.tissue_contours,
                                              color_dict=self.tissue_color_dict,
                                              types=self.tissue_type,
                                              show_types=list(showType) if len(showType) != 0 else None,
                                              remove_types=list(removeType) if len(removeType) != 0 else None)


    def show_nucleus_diff_slot(self, showItem, clear_nucleus=False):
        """
            Args:showItem: 是一个列表，存放了要显示的差异细胞中心点["FP"， "FN", ...] or []
        """
        if self.nucleus_diff is None or self.nucleus_diff_properties is None or self.nucleus_center is None:
            return
        showItem = set(showItem)
        removeType = self.showItemNucleusDiff - showItem
        self.showItemNucleusDiff = showItem
        if clear_nucleus:
            self.NucleusMarkLoader.last_nucleus = None
        self.NucleusMarkLoader.load_nucleus_mark(current_rect=self.get_current_view_scene_rect(),
                                                 current_level=self.current_level,
                                                 current_downsample=self.current_downsample,
                                                 centers=self.nucleus_center,
                                                 nucleus_marks=self.nucleus_diff,
                                                 color_dict=self.nucleus_diff_color_dict,
                                                 show_types=showItem,
                                                 remove_types=removeType)

    def show_grid_slot(self, is_show, patch_size=None, stride=None, Opacity=None):
        dimension_X, dimension_Y = self.slide_helper.level_dimensions[0]
        self.PatchLineLoader.load_line(dimension_X, dimension_Y,
                                       current_level=self.current_level,
                                       current_downsample=self.current_downsample,
                                       patch_size=patch_size,
                                       stride=stride,
                                       Opacity=Opacity,
                                       show=is_show)

    def show_nuclei(self):
        """
            当视图移动，视图缩放等操作的时候，要加载未载入到当前视图中的细胞核轮廓
        """
        if self.nucleus_contour is not None and self.nucleus_center is not None and self.nucleus_type is not None:
            showItem = []
            for type_idx in self.showItemNucleus:
                for type_name, item in self.nucleus_properties.items():
                    if type_idx == item["type"]:
                        showItem.append(type_name)
                        break
            self.show_nucleus_slot(showItem)

        self.show_nucleus_diff_slot(self.showItemNucleusDiff)

    def show_contour(self):
        """
            当视图缩放等操作的时候，要加载区域轮廓
        """
        if self.tissue_contours is None or self.tissue_properties is None or self.tissue_type is None:
            return

        showItem = []
        for type_idx in self.showItemTissueContour:
            for type_name, item in self.tissue_properties.items():
                if type_idx == item["type"]:
                    showItem.append(type_name)
                    break
        self.show_contour_slot(showItem, True)

    def show_line(self):
        self.show_grid_slot(self.PatchLineLoader.show)

    def reset_load_nucleus(self):
        """
            scence.clear后需要将载入的细胞给清空
        """
        self.NucleiContourLoader.last_nuclei = None
        self.NucleusMarkLoader.last_nucleus = None

    def reshowView(self, heatmap=None, heatmap_downsample=None):
        super().reshowView(heatmap, heatmap_downsample)
        self.reset_load_nucleus()
        self.show_nuclei()
        self.show_contour()
        self.show_line()

    def addContourItem(self, item):
        """
            向场景中添加组织轮廓
        """
        if item.level != self.current_level:
            return
        self.scene.addItem(item)

    def removeContourItem(self, item):
        """
            将场景中的某个组织轮廓删除
        """
        self.scene.removeItem(item)

    # 修改细胞核的类型
    def modify_nucleus(self, event_point):
        if self.mainViewerFlag is False:
            return False
        if self.nucleus_center is None or self.nucleus_properties is None:
            return False
        items = self.view.items(event_point)
        if items is None:
            return False

        flag = False
        for item in items:
            if hasattr(item, "is_contour") and hasattr(item, "is_region"):
                if item.is_region:
                    return False
                else:
                    flag = True
                    break
        if flag is False:
            return False

        # 获取与之对应的细胞核
        point = self.view.mapToScene(event_point)
        distance = np.square(np.array([point.x()]) - self.nucleus_center[:, 0]) + np.square(np.array([point.y()]) - self.nucleus_center[:, 1])
        nucleus_idx = np.where(distance == distance.min())[0]
        nucleus_contour = self.nucleus_contour[nucleus_idx][0]
        # 判断细胞是否在轮廓内
        if cv2.pointPolygonTest(nucleus_contour, (int(point.x()), int(point.y())), False) <= 0:
            return False

        from window.dialog.changeNucleusDialog import ChangeNucleusDiaglog
        dialog = ChangeNucleusDiaglog(self.nucleus_properties)
        if dialog.exec_() != QDialog.Accepted:
            return True

        self.modify_nucleus_flag = True
        nucleus_type_name = dialog.get_text()
        nucleus_type = self.nucleus_properties[nucleus_type_name]["type"]
        nucleus_color = self.nucleus_properties[nucleus_type_name]["color"]
        self.nucleus_type[nucleus_idx] = -nucleus_type
        # 绘制标注
        annotation_item, control_point_items, text_item = self.ToolManager.draw_polygon.draw(nucleus_contour, QColor(*nucleus_color), 1, self.current_downsample, True)
        annotation = {
            "location": nucleus_contour.tolist(),
            "color": nucleus_color,
            "tool": "多边形",
            "type": nucleus_type_name,
            "annotation_item": annotation_item,
            "control_point_items": control_point_items,
            "text_item": text_item
        }
        self.ToolManager.addAnnotation(annotation, self.current_downsample)
        self.scene.removeItem(item)
        # item.set_path_item_pen(nucleus_color, 3)
        return True

    # 更改heatmap权重
    def change_heatmap_alpha(self):
        from window.slide_window.utils.heatmap_alpha_slider import heatmap_alpha_Dialog
        dialog = heatmap_alpha_Dialog(self.heatmap_alpha)
        # 显示对话框
        result = dialog.exec_()
        # 在确定按钮点击后，输出滑块的值
        if result == QDialog.Accepted:
            self.heatmap_alpha = dialog.get_slider_value()
            self.TileLoader.change_heatmap_alpha(self.heatmap_alpha)

    def save_nucleus_info(self):
        if self.modify_nucleus_flag is False or self.nucleus_properties is None or self.mainViewerFlag is False:
            return
        from window.dialog.AffirmDialog import CloseDialog
        text = f"是否保存窗口{self.slide_name}的细胞核结果"
        dialog = CloseDialog(text)
        if dialog.exec_() != QDialog.Accepted:
            return
        options = QFileDialog.Options()
        path, _ = QFileDialog.getSaveFileName(self, '保存细胞核分割结果',
                                              f'{constants.micro_path}/{self.slide_name}_nucleus.pkl',
                                              'PKL Files(*.pkl)', options=options)
        if path == "":
            return
        from function.check_write_permission import check_write_permission
        permission = check_write_permission(os.path.dirname(path))
        if permission is False:
            QMessageBox.warning(self, "警告", "该文件夹没有写权限！")
            return
        nucleus_info = {"properties": {"nucleus_info": self.nucleus_properties},
                        "nucleus_info": {
                            "type": self.nucleus_type,
                            "center": self.nucleus_center,
                            "contour": self.nucleus_contour
                        }}
        with open(path, 'wb') as f:
            pickle.dump(nucleus_info, f)
            f.close()

    def closeEvent(self, *args, **kwargs):
        if self.mainViewerFlag:
            self.save_nucleus_info()
        if hasattr(self, "TileLoader"):
            self.scene.clear()
            self.TileLoader.__del__()
            print("closeEvent")
        del self.nucleus_center
        del self.nucleus_contour
        del self.nucleus_type
        del self.nucleus_properties
        del self.nucleus_diff
        del self.heatmap
        del self.tissue_contours
        del self.tissue_type
        self.NucleiContourLoader.__del__()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SlideViewer()
    window.show()
    sys.exit(app.exec_())

