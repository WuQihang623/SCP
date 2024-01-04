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
from function.heatmap_background import get_colormap_background, numpy_to_pixmap
from window.slide_window.BasicSlideViewer import BasicSlideViewer
from window.slide_window.Tools import ToolManager
from window.slide_window.TileLoader.RegionContourLoader import RegionContourLoader
from window.slide_window.TileLoader.NucleiContourLoader import NucleiContourLoader
from window.slide_window.utils.ChangeAnnotationDialog import ChangeAnnotationDiaglog

class SlideViewer(BasicSlideViewer):
    # 发送激活标注的索引信号
    reactivateItemSignal = pyqtSignal(int, float)

    # 发送给微环境分析面板，细胞个数的信号
    sendNucleiNumMicroenvSignal = pyqtSignal(list)
    # 发送给微环境分析面板，设置显示哪几种组织区域
    sendRegionShowTypeMicroenvSignal = pyqtSignal(list)
    # 发送给微环境分析面板，设置是否要显示(组织区域，热图，细胞核）
    sendShowMicroenvSignal = pyqtSignal(list)
    # 发送给微环境分析面板，设置显示是否要显示表皮细胞，淋巴细胞
    sendNucleiShowTypeMicroenvSignal = pyqtSignal(list)

    # 发送给PDL1面板，细胞个数的信号
    sendNucleiNumPDL1Signal = pyqtSignal(list)
    # 发送给PDL1面板，设置是否要显示(组织区域，热图，细胞核）
    sendShowPDL1Signal = pyqtSignal(list)
    # 发送给PDL1分析面板，设置显示哪几种组织区域
    sendRegionShowTypePDL1Signal = pyqtSignal(list)
    # 发送给PDL1分析面板，设置显示是否要显示表皮细胞，淋巴细胞
    sendNucleiShowTypePDL1Signal = pyqtSignal(list)
    def __init__(self, paired=False):
        super(SlideViewer, self).__init__()
        # 初始化标注工具,同步窗口并不需要标注工具
        self.paired = paired
        self.init_ToolManager()

        # 组织区域轮廓加载器
        self.RegionContourLoader = RegionContourLoader(scene=self.scene)
        self.RegionContourLoader.addContourItemSignal.connect(self.addContourItem)
        self.RegionContourLoader.removeItemSignal.connect(self.removeContourItem)
        # 细胞核轮廓加载器
        self.NucleiContourLoader = NucleiContourLoader(scene=self.scene)

    def init_variable(self):
        super(SlideViewer, self).init_variable()
        """
        0:  显示标注
        1： 显示诊断结果
        2： 显示微环境分析
        3： 显示PD-L1分析
        4:  显示多模态分析
        """
        self.SHOW_FLAG = 0
        # 初始化诊断框
        self.diagnose_rects = []

        # 肿瘤微环境分析变量
        self.heatmap_microenv = None
        self.heatmap_downsample_microenv = None
        self.micrienv_colormap = None
        self.tissue_contours_microenv = None
        self.tissue_colors_microenv = None
        self.tissue_class_microenv = None
        self.cell_type_microenv = None
        self.cell_centers_microenv = None
        self.cell_contour_microenv = None

        # PDL1分析变量
        self.heatmap_pdl1 = None
        self.heatmap_downsample_pdl1 = None
        self.tissue_contours_pdl1 = None
        self.tissue_colors_pdl1 = None
        self.tissue_class_pdl1 = None
        self.cell_type_pdl1 = None
        self.cell_centers_pdl1 = None
        self.cell_contour_pdl1 = None

        # 在标注模式下载入细胞核分割结果
        self.cell_type_ann = None
        self.cell_centers_ann = None
        self.cell_contour_ann = None

        # 要显示的组织轮廓类型
        self.show_region_types_microenv = []
        self.show_region_types_pdl1 = []
        # 显示组织轮廓标志
        self.show_microenv_region_contour_flag = False
        self.show_pdl1_region_contour_flag = False

        # 要显示的细胞核类型
        self.show_nuclei_types_microenv = []
        self.show_nuclei_types_pdl1 = []
        # 显示细胞轮廓标志
        self.show_microenv_nuclei_flag = False
        self.show_pdl1_nuclei_flag = False
        self.show_ann_nuclei_flag = False
        # 显示细胞核的颜色
        self.nuclei_type_dict = {0: [166, 84, 2], 1: [255, 0, 0], 2: [0, 255, 0], 3: [228, 252, 4], 4: [0, 0, 255]}

        # 当前要显示的内容
        self.show_list_microenv = []
        self.show_list_pdl1 = []

        # 显示heatmap map还是hierarchy mask
        self.show_micrienv_colormap_flag = False
        self.show_hierarchy_checkbox_state = False

    # 初始化标注工具
    def init_ToolManager(self):
        self.ToolManager = ToolManager(self.view, self.scene)

    # 载入slide
    def load_slide(self, slide_path, zoom_step=1.25):
        super(SlideViewer, self).load_slide(slide_path, zoom_step)
        # 设置测量工具的mpp
        self.ToolManager.measure_tool.set_mpp(self.slide_helper.mpp)
        self.load_nuclues_action.triggered.connect(self.choose_pkl_file)
        self.change_heatmap_alpha_action.triggered.connect(self.change_heatmap_alpha)

    def eventFilter(self, qobj: 'QObject', event: 'QEvent') -> bool:
        # 如果不是鼠标事件或者滚轮事件，则不进行事件的传递
        event_porcessed = False
        # 鼠标事件
        if isinstance(event, QMouseEvent):
            event_porcessed = self.processMouseEvent(event)
        elif isinstance(event, QWheelEvent):
            event_porcessed = self.processWheelEvent(event)
        return event_porcessed

    # 鼠标事件
    def processMouseEvent(self, event: QMouseEvent):
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
                if hasattr(self, 'ToolManager') and self.show_ann_nuclei_flag:
                    if self.ToolManager.TOOL_FLAG == 1:
                        reply = self.modify_nuclei(event.pos())
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
            if (self.move_flag and self.move_allow_flag):
                self.responseMouseMove(event)
            else:
                self.ToolManager.mouseMoveEvent(event, self.current_downsample)
            # 同步图像的鼠标绘制
            if self.Registration:
                pos = self.view.mapToScene(event.pos())
                self.pairMouseSignal.emit(pos)
        return True

    # 鼠标拖动页面
    def responseMouseMove(self, event):
        super().responseMouseMove(event)
        # 绘制细胞核分割结果
        self.show_nuclei()

    # 鼠标滚轮操作
    def responseWheelEvent(self, mousePos: QPoint, zoom):
        super().responseWheelEvent(mousePos, zoom)
        # 显示细胞核轮廓
        self.show_nuclei()

    def update_scale_view(self, level, scene_view_rect, clear_scene_flag, mouse_pos):
        # 更新图像视图
        super(SlideViewer, self).update_scale_view(level, scene_view_rect, clear_scene_flag, mouse_pos)
        if clear_scene_flag:
            downsample = self.slide_helper.get_downsample_for_level(level)
            # 重新绘制标注
            # 如果在标注模式下，重新绘制当前的标注
            if self.SHOW_FLAG == 0:
                self.ToolManager.redraw(level, downsample)
            # 重新绘制诊断框
            if self.SHOW_FLAG == 1:
                self.redrawDiagnoseRect()
            # 重新绘制细胞核分割结果，肿瘤区域分割结果
            if self.SHOW_FLAG == 2:
                self.show_or_close_contour(self.tissue_contours_microenv,
                                           self.tissue_colors_microenv,
                                           self.tissue_class_microenv,
                                           self.show_region_types_microenv)
            elif self.SHOW_FLAG == 3:
                self.show_or_close_contour(self.tissue_contours_pdl1,
                                           self.tissue_colors_pdl1,
                                           self.tissue_class_pdl1,
                                           self.show_region_types_pdl1,
                                           Microenv=False)
            elif self.SHOW_FLAG == 4:
                # 并不要重新绘制什么上去
                pass

    # 导入标注时重新绘制所有的标注
    def loadAllAnnotation(self):
        # downsample = self.slide_helper.get_downsample_for_level(self.current_level)
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

    # 跳转到当前level下的以pos为中心的区域
    def switch2pos(self, pos):
        super().switch2pos(pos)
        self.show_nuclei()

    # 点击缩略图，跳转到对应区域
    def showImageAtThumbnailArea(self, pos, thumbnail_dimension):
        super(SlideViewer, self).showImageAtThumbnailArea(pos, thumbnail_dimension)
        # self.show_nuclei()

    # 响应slider动作
    def responseSlider(self, value):
        super(SlideViewer, self).responseSlider(value)

    # TODO：加载诊断模式的结果
    def load_diagnose(self, path):
        with open(path, 'rb') as f:
            results = pickle.load(f)
            f.close()
        self.overview_diagnose = numpy_to_pixmap(results['image'])
        self.heatmap_downsample_diagnose = results["preds"]['down']
        self.heatmap_diagnose = results["heatmap"]
        self.heatmap = self.heatmap_diagnose.copy()
        self.heatmap_downsample = self.heatmap_downsample_diagnose
        # 显示热图
        self.TileLoader.update_heatmap_background(self.overview_diagnose)

    # 实现诊断模式的热图显示或关闭，以及高质量预测框的显示
    def show_or_close_diagnose_heatmap(self, flag):
        if not hasattr(self, 'heatmap_diagnose') or not hasattr(self, 'heatmap_downsample_diagnose'):
            QMessageBox.warning(self, '警告', "没有载入诊断结果！")
            return
        # 更新thumbnail,再更新heatmap
        if flag:
            self.thumbnail.load_thumbnail(self.slide_helper, self.overview_diagnose)
            self.heatmap = self.heatmap_diagnose.copy()
            self.heatmap_downsample = self.heatmap_downsample_diagnose
            self.reshowView(self.heatmap, self.heatmap_downsample)
        else:
            self.thumbnail.load_thumbnail(self.slide_helper)
            self.heatmap = None
            self.heatmap_downsample = None
            self.reshowView()
        self.redrawDiagnoseRect()

    # 重新绘制诊断的矩形框（当缩放时）
    def redrawDiagnoseRect(self):
        # downsample = self.slide_helper.get_downsample_for_level(self.current_level)
        pen = QPen()
        pen.setColor(QColor(Qt.blue))
        pen.setWidth(4)
        self.diagnose_rect_items = []
        for rect in self.diagnose_rects:
            x = rect[0] / self.current_downsample
            y = rect[1] / self.current_downsample
            width = rect[2] / self.current_downsample
            height = rect[3] / self.current_downsample
            rect_item = QGraphicsRectItem()
            rect_item.setPen(pen)
            rect_item.setRect(x, y, width, height)
            rect_item.setZValue(100)
            self.scene.addItem(rect_item)
            self.diagnose_rect_items.append(rect_item)

    # 切换模式时，删除掉诊断框
    def removeDiagnoseRect(self):
        if hasattr(self, 'diagnose_rect_items'):
            for item in self.diagnose_rect_items:
                try:
                    self.scene.removeItem(item)
                except:
                    pass

    # 获取诊断框信息
    def receiveDiagnoseRect(self, rect_list):
        self.diagnose_rects = rect_list
        self.redrawDiagnoseRect()

    # 将视野移动到诊断框上
    def move2DiagnoseRect(self, idx):
        if self.diagnose_rects:
            # 调整缩放倍数到40
            self.responseSlider(40)

            rect = self.diagnose_rects[idx]
            # downsample = self.slide_helper.get_downsample_for_level(self.current_level)
            # 要将pos设置为scene的中心
            pos = QPointF(rect[0] / self.current_downsample + rect[2] / 2 / self.current_downsample, rect[1] / self.current_downsample + rect[3] / 2 / self.current_downsample)
            self.view.centerOn(pos)
            self.view.update()

            # 获取当前视图在场景中的矩形
            view_scene_rect = self.get_current_view_scene_rect()
            # 加载当前视图内可见的图块
            self.TileLoader.load_tiles_in_view(self.current_level, view_scene_rect, self.heatmap,
                                               self.heatmap_downsample)
            # 发射FOV更新信号
            self.updateFOVSignal.emit(view_scene_rect, self.current_level)

            # 更新状态栏,视图位置
            self.magnificationSignal.emit(True)

            # 将上一个诊断框颜色置为黑色
            if hasattr(self, 'diagnose_rect_items'):
                for rect_item in self.diagnose_rect_items:
                    rect_item.setPen(QPen(Qt.blue))
                self.diagnose_rect_items[idx].setPen(QPen(Qt.red))

    # 向场景中添加组织轮廓
    def addContourItem(self, item):
        if item.level != self.current_level:
            return
        self.scene.addItem(item)

    # 将场景中的某个组织轮廓删除
    def removeContourItem(self, item):
        self.scene.removeItem(item)

    def loadRegistrationWSIInfo(self, WSI_Info: dict):
        """显示配准的细胞核分割结果
        载入文件的格式:
            {
                "type": ndarray,
                "center": ndarray,
                "contour": ndarray,
                "grid": ndarray,
            }
        """

        # 如果还没有载入视图，则不进行显示
        if not hasattr(self, "slide"):
            return

        self.sendShowMicroenvSignal.emit([])
        self.sendRegionShowTypeMicroenvSignal.emit([])

        # 载入细胞核分割结果
        self.cell_centers_microenv = WSI_Info['center']
        self.cell_type_microenv = WSI_Info['type']
        self.cell_contour_microenv = WSI_Info['contour']

        self.tissue_contours_microenv = WSI_Info["grid"]
        self.tissue_colors_microenv = np.zeros((WSI_Info["grid"].shape[0], 3))
        self.tissue_class_microenv = np.ones(WSI_Info["grid"].shape[0]) * 5

        # 发送信号，给Combox，设置显示细胞核轮廓， （表皮细胞， 淋巴细胞……）
        self.sendShowMicroenvSignal.emit([1, 2])
        self.sendRegionShowTypeMicroenvSignal.emit([4])
        self.sendNucleiShowTypeMicroenvSignal.emit([0, 1, 2, 3, 4])

    # 加载微环境分析结果
    def loadMicroenv(self, path):
        try:
            with open(path, 'rb') as f:
                microenv_info = pickle.load(f)
                f.close()
        except:
            QMessageBox.warning(self, '警告', '微环境分析结果有误')
            return
        # 发送要显示组织区域与细胞核轮廓的变量
        sendShowMicroenv = []

        # 初始化checkbox
        self.sendShowMicroenvSignal.emit(sendShowMicroenv)
        self.sendRegionShowTypeMicroenvSignal.emit([])
        self.sendNucleiShowTypeMicroenvSignal.emit([])

        # 加载肿瘤区域结果
        if microenv_info.get('mask') is None:
            QMessageBox.warning(self, '提示', '该文件中没有肿瘤区域分割结果！')
        elif isinstance(microenv_info['mask'], np.ndarray):
            if microenv_info.get('region_contours') is None or microenv_info.get('region_colors') is None or microenv_info.get('region_types') is None:
                pass
            else:
                self.tissue_contours_microenv = microenv_info.get('region_contours')
                self.tissue_colors_microenv = microenv_info.get('region_colors')
                self.tissue_class_microenv = microenv_info.get('region_types')

            try:
                # 用于保存肿瘤微环境分析的热图
                if len(microenv_info['mask'].shape) == 2:
                    self.heatmap_microenv = np.zeros((*microenv_info['mask'].shape, 3), dtype=np.uint8)
                    color_list = [[0, 0, 0], [0, 0, 255], [255, 0, 0], [0, 255, 0], [255, 255, 255]]
                    for i in range(1, 5):
                        self.heatmap_microenv[microenv_info['mask']==i, :] = color_list[i]
                elif len(microenv_info['mask'].shape) == 3:
                    self.heatmap_microenv = microenv_info['mask']
                else:
                    QMessageBox.warning(self, "提示", "语义分割结果的格式错误！")
                self.heatmap_downsample_microenv = int(microenv_info['heatmap_downsample'])
                if self.show_hierarchy_checkbox_state is False:
                    self.show_micrienv_colormap_flag = False
                    self.TileLoader.update_heatmap_background(self.heatmap_microenv, self.heatmap_alpha, self.heatmap_downsample_microenv)
                    sendShowMicroenv.append(0)
            except:
                QMessageBox.warning(self, "提示", "colormap加载出错！")
        else:
            QMessageBox.warning(self, "提示", "语义分割结果的格式错误！")

        # 加载层级结果
        if microenv_info.get('hierarchy_mask') is not None:
            if len(microenv_info['hierarchy_mask'].shape) == 3:
                self.micrienv_colormap = microenv_info['hierarchy_mask']
                if self.show_hierarchy_checkbox_state is True:
                    self.show_micrienv_colormap_flag = True
                    self.TileLoader.update_heatmap_background(self.micrienv_colormap, self.heatmap_alpha, self.heatmap_downsample_microenv)
                    sendShowMicroenv.append(0)
            else:
                QMessageBox.warning(self, "提示", "层级区域的格式错误！")

        # 加载细胞核分割结果
        try:
            self.cell_centers_microenv = microenv_info['center']
            self.cell_type_microenv = microenv_info['type']
            self.cell_contour_microenv = microenv_info['contour']
            # TODO: 发送信号，给Combox，设置显示细胞核轮廓， （表皮细胞， 淋巴细胞……）
            sendShowMicroenv.append(2)

            # 细胞计数
            if self.paired is False:
                num_list = self.count_cells(self.cell_type_microenv)
                self.sendNucleiNumMicroenvSignal.emit(num_list)
        except:
            QMessageBox.warning(self, '警告', '该文件中没有细胞核分割结果！')

        self.sendShowMicroenvSignal.emit(sendShowMicroenv)
        if 1 in sendShowMicroenv:
            self.sendRegionShowTypeMicroenvSignal.emit([0, 2, 3])
        if 2 in sendShowMicroenv:
            self.sendNucleiShowTypeMicroenvSignal.emit([0, 1, 2, 3, 4])

    def loadPDL1(self, path):
        try:
            with open(path, 'rb') as f:
                pdl1_info = pickle.load(f)
                f.close()
        except:
            QMessageBox.warning(self, '警告', 'PD-L1分析结果有误')
            return

        # 发送要显示组织区域与细胞核轮廓的变量
        sendShowPDL1 = []
        self.sendShowPDL1Signal.emit(sendShowPDL1)
        self.sendRegionShowTypePDL1Signal.emit([])
        self.sendNucleiShowTypePDL1Signal.emit([])

        # 加载肿瘤区域结果
        if pdl1_info.get('mask') is None:
            QMessageBox.warning(self, '提示', '该文件中没有肿瘤区域分割结果！')
        else:
            if pdl1_info.get('region_contours') is None or pdl1_info.get('region_colors') is None or \
                    pdl1_info.get('region_types') is None:
                pass
            else:
                self.tissue_contours_pdl1 = pdl1_info.get('region_contours')
                self.tissue_colors_pdl1 = pdl1_info.get('region_colors')
                self.tissue_class_pdl1 = pdl1_info.get('region_types')
                # TODO: 发送信号，给Combox，设置显示组织轮廓，（肿瘤，基质）
                # sendShowPDL1.append(1)

            try:
                # 用于保存PDL1分析的colormap
                if len(pdl1_info['mask'].shape) == 2:
                    self.heatmap_pdl1 = np.zeros((*pdl1_info['mask'].shape, 3), dtype=np.uint8)
                    color_list = [[0, 0, 0], [255, 0, 0]]
                    for i in range(1, 2):
                        self.heatmap_pdl1[pdl1_info['mask']==i, :] = color_list[i]
                elif len(pdl1_info['mask'].shape) == 3:
                    self.heatmap_pdl1 = pdl1_info['mask']
                else:
                    QMessageBox.warning(self, "提示", "语义分割结果的格式错误！")
                self.heatmap_downsample_pdl1 = int(pdl1_info['heatmap_downsample'])
                self.TileLoader.update_heatmap_background(self.heatmap_pdl1, self.heatmap_alpha, self.heatmap_downsample_pdl1)
                sendShowPDL1.append(0)
            except:
                QMessageBox.warning(self, "提示", "colormap加载出错！")

        # 加载细胞核分割结果
        try:
            self.cell_centers_pdl1 = pdl1_info['center']
            self.cell_type_pdl1 = pdl1_info['type']
            self.cell_contour_pdl1 = pdl1_info['contour']
            # TODO: 发送信号，给Combox，设置显示细胞核轮廓， （表皮细胞， 淋巴细胞……）
            sendShowPDL1.append(2)

            # 细胞计数
            if self.paired is False:
                num_list = self.count_cells(self.cell_type_pdl1)
                self.sendNucleiNumPDL1Signal.emit(num_list)
        except:
            QMessageBox.warning(self, '警告', '该文件中没有细胞核分割结果！')

        self.sendShowPDL1Signal.emit(sendShowPDL1)
        if 1 in sendShowPDL1:
            self.sendRegionShowTypePDL1Signal.emit([0])
        if 2 in sendShowPDL1:
            self.sendNucleiShowTypePDL1Signal.emit([0, 1, 2, 3, 4])

    def choose_pkl_file(self):
        """
            鼠标右击视图，弹出的菜单中，响应载入细胞核分割结果
        """
        options = QFileDialog.Options()
        path, _ = QFileDialog.getOpenFileName(self, "选择细胞核分割结果", './',
                                              "标注 (*.pkl)", options=options)
        slide_name, _ = os.path.splitext(os.path.basename(self.slide_helper.slide_path))
        if os.path.exists(path):
            if slide_name in path:
                self.loadNuclei(path)
            else:
                QMessageBox.warning(self, '警告', '导入文件与当前图片不符')

    # 在标注模式下导入细胞核分割结果
    def loadNuclei(self, path):
        try:
            with open(path, 'rb') as f:
                nuclei_info = pickle.load(f)
                f.close()
        except:
            QMessageBox.warning(self, '警告', '细胞核结果有误')
            return

        # 加载细胞核分割结果
        try:
            self.cell_centers_ann = nuclei_info['center']
            self.cell_type_ann = nuclei_info['type']
            self.cell_contour_ann = nuclei_info['contour']
            self.reverse_nulei(True)
        except:
            QMessageBox.warning(self, '警告', '该文件中没有细胞核分割结果！')

    # 显示或关闭标注模式下的细胞核分割结果
    def reverse_nulei(self, flag):
        if self.cell_contour_ann is not None and self.cell_type_ann is not None and self.cell_centers_ann is not None:
            self.show_ann_nuclei_flag = flag
            self.show_or_close_nuclei(current_rect=self.get_current_view_scene_rect(),
                                      contours=self.cell_contour_ann,
                                      centers=self.cell_centers_ann,
                                      types=self.cell_type_ann,
                                      color_dict=self.nuclei_type_dict,
                                      show_types=[0, 1, 2, 3, 4],
                                      mode=0)

    # 细胞类型计数
    def count_cells(self, cell_type):
        num1 = (cell_type == 1).sum()
        num2 = (cell_type == 2).sum()
        num3 = (cell_type == 3).sum()
        num4 = (cell_type == 4).sum()
        return [num1, num2, num3, num4]

    # TODO：切换层级结构图与region map
    def change_hierarchy_mask_and_region_mask(self, to_hierarchy_mask):
        if to_hierarchy_mask == 2:
            self.show_hierarchy_checkbox_state = True
        else:
            self.show_hierarchy_checkbox_state = False
        if self.micrienv_colormap is not None and self.heatmap_microenv is not None and \
            self.heatmap_downsample is not None and self.heatmap is not None:
            downsample = self.heatmap_downsample
            self.show_or_close_heatmap(None, None, False)
            self.TileLoader.loaded_heatmapItem = []
            if to_hierarchy_mask == 2:
                self.show_micrienv_colormap_flag = True
                self.TileLoader.update_heatmap_background(self.micrienv_colormap, self.heatmap_alpha, self.heatmap_downsample)
                self.show_or_close_heatmap(self.micrienv_colormap, downsample, True)
            else:
                self.show_micrienv_colormap_flag = False
                self.TileLoader.update_heatmap_background(self.heatmap_microenv, self.heatmap_alpha, self.heatmap_downsample)
                self.show_or_close_heatmap(self.heatmap_microenv, downsample, True)
            self.NucleiContourLoader.last_level = -1
            self.show_or_close_nuclei(current_rect=self.get_current_view_scene_rect(),
                                      contours=self.cell_contour_microenv,
                                      centers=self.cell_centers_microenv,
                                      types=self.cell_type_microenv,
                                      color_dict=self.nuclei_type_dict,
                                      show_types=self.show_nuclei_types_microenv)

    # TODO: 加载肿瘤微环境或者PDL1热图
    def show_or_close_heatmap(self, heatmap, heatmap_downsample, flag):
        # 更新heatmap
        if flag:
            self.heatmap = heatmap
            self.heatmap_downsample = heatmap_downsample
            self.reshowView(self.heatmap, self.heatmap_downsample)
        else:
            self.heatmap = None
            self.heatmap_downsample = None
            self.reshowView()

    # 更新要显示的肿瘤微环境组织区域类型,连接showRegionType_Combox
    def update_show_region_types_microenv(self, type_list):
        type_dict = {"基质区域": 1, "肿瘤区域": 2, "坏死区域": 3, "无关区域": 4, "图像块": 5}
        new_show_types = []
        for type in type_list:
            if type_dict.get(type) is not None:
                new_show_types.append(type_dict.get(type))
        new_show_types = set(new_show_types)
        remove_types = set(self.show_region_types_microenv) - new_show_types
        self.show_region_types_microenv = new_show_types
        self.show_or_close_contour(self.tissue_contours_microenv,
                                   self.tissue_colors_microenv,
                                   self.tissue_class_microenv,
                                   self.show_region_types_microenv,
                                   remove_types)

    # 更新要显示的PDL1组织区域类型,连接showRegionType_Combox
    def update_show_region_types_pdl1(self, type_list):
        type_dict = {"肿瘤区域": 1}
        new_show_types = []
        for type in type_list:
            if type_dict.get(type) is not None:
                new_show_types.append(type_dict.get(type))
        new_show_types = set(new_show_types)
        remove_types = set(self.show_region_types_pdl1) - new_show_types
        self.show_region_types_pdl1 = new_show_types
        self.show_or_close_contour(contours=self.tissue_contours_pdl1,
                                   colors=self.tissue_colors_pdl1,
                                   types=self.tissue_class_pdl1,
                                   show_types=self.show_region_types_pdl1,
                                   remove_types=remove_types, Microenv=False)

    # TODO: 加载或关闭肿瘤微环境或PDL1组织区域轮廓显示
    def show_or_close_contour(self, contours, colors, types, show_types, remove_types=None, Microenv=True):
        if Microenv:
            flag = self.show_microenv_region_contour_flag
        else:
            flag = self.show_pdl1_region_contour_flag
        if flag:
            self.RegionContourLoader.load_contour(current_level=self.current_level,
                                                  current_downsample=self.slide_helper.get_downsample_for_level(self.current_level),
                                                  contours=contours,
                                                  colors=colors,
                                                  types=types,
                                                  show_types=show_types,
                                                  remove_types=remove_types)
        # 如果不显示组织轮廓，则把已经添加的item删除
        else:
            self.RegionContourLoader.load_contour(current_level=self.current_level,
                                                  current_downsample=self.slide_helper.get_downsample_for_level(self.current_level),
                                                  contours=None,
                                                  colors=None,
                                                  types=None,
                                                  show_types=None,
                                                  remove_types=[1, 2, 3, 4])

    # 更新要显示的肿瘤微环境细胞核类型,连接showNucleiType_Combox
    def update_show_nuclei_types_microenv(self, type_list):
        type_dict = {"背景类别": 0, "表皮细胞": 1, "淋巴细胞": 2, "中性粒细胞": 4, "基质细胞": 3}
        new_show_types = []
        for type in type_list:
            if type_dict.get(type) is not None:
                new_show_types.append(type_dict.get(type))
        new_show_types = set(new_show_types)
        remove_types = set(self.show_nuclei_types_microenv) - new_show_types
        self.show_nuclei_types_microenv = new_show_types
        self.NucleiContourLoader.last_nuclei = None
        self.show_or_close_nuclei(current_rect=self.get_current_view_scene_rect(),
                                  contours=self.cell_contour_microenv,
                                  centers=self.cell_centers_microenv,
                                  types=self.cell_type_microenv,
                                  color_dict=self.nuclei_type_dict,
                                  show_types=self.show_nuclei_types_microenv,
                                  remove_types=remove_types)

    # 更新要显示的PDL1细胞核类型,连接showNucleiType_Combox
    def update_show_nuclei_types_pdl1(self, type_list):
        type_dict = {"背景类别": 0, "PD-L1阳性肿瘤细胞": 1, "PD-L1阴性肿瘤细胞": 2, "PD-L1阳性免疫细胞": 3, "PD-L1阴性免疫细胞": 4}
        new_show_types = []
        for type in type_list:
            if type_dict.get(type) is not None:
                new_show_types.append(type_dict.get(type))
        new_show_types = set(new_show_types)
        remove_types = set(self.show_nuclei_types_pdl1) - new_show_types
        self.show_nuclei_types_pdl1 = new_show_types
        self.NucleiContourLoader.last_nuclei = None
        self.show_or_close_nuclei(current_rect=self.get_current_view_scene_rect(),
                                  contours=self.cell_contour_pdl1,
                                  centers=self.cell_centers_pdl1,
                                  types=self.cell_type_pdl1,
                                  color_dict=self.nuclei_type_dict,
                                  show_types=self.show_nuclei_types_pdl1,
                                  remove_types=remove_types, mode=3)

    # TODO: 加载或关闭肿瘤微环境或PDL1细胞核轮廓
    def show_or_close_nuclei(self, current_rect, contours, centers, types, color_dict, show_types, remove_types=None, mode=2):
        if mode == 2:
            flag = self.show_microenv_nuclei_flag
        elif mode == 3:
            flag = self.show_pdl1_nuclei_flag
        elif mode == 0:
            flag = self.show_ann_nuclei_flag
        else:
            return
        if flag:
            self.NucleiContourLoader.load_contour(current_rect=current_rect,
                                                  current_level=self.current_level,
                                                  current_downsample=self.slide_helper.get_downsample_for_level(
                                                      self.current_level),
                                                  contours=contours,
                                                  centers=centers,
                                                  types=types,
                                                  color_dict=color_dict,
                                                  show_types=show_types,
                                                  remove_types=remove_types)
        else:
            if contours is not None:
                self.NucleiContourLoader.last_nuclei = None
                self.NucleiContourLoader.load_contour(current_rect=current_rect,
                                                      current_level=self.current_level,
                                                      current_downsample=self.slide_helper.get_downsample_for_level(self.current_level),
                                                      contours=None,
                                                      centers=None,
                                                      types=None,
                                                      color_dict=color_dict,
                                                      show_types=show_types,
                                                      remove_types=[0, 1, 2, 3, 4])

    def show_nuclei(self):
        """
            当视图移动，视图缩放等操作的时候，要加载未载入到当前视图中的细胞核轮廓
        """
        if self.SHOW_FLAG == 2:
            self.show_or_close_nuclei(current_rect=self.get_current_view_scene_rect(),
                                      contours=self.cell_contour_microenv,
                                      centers=self.cell_centers_microenv,
                                      types=self.cell_type_microenv,
                                      color_dict=self.nuclei_type_dict,
                                      show_types=self.show_nuclei_types_microenv)
        elif self.SHOW_FLAG == 3:
            self.show_or_close_nuclei(current_rect=self.get_current_view_scene_rect(),
                                      contours=self.cell_contour_pdl1,
                                      centers=self.cell_centers_pdl1,
                                      types=self.cell_type_pdl1,
                                      color_dict=self.nuclei_type_dict,
                                      show_types=self.show_nuclei_types_pdl1,
                                      mode=3)
        elif self.SHOW_FLAG == 0:
            self.show_or_close_nuclei(current_rect=self.get_current_view_scene_rect(),
                                      contours=self.cell_contour_ann,
                                      centers=self.cell_centers_ann,
                                      types=self.cell_type_ann,
                                      color_dict=self.nuclei_type_dict,
                                      show_types=[0, 1, 2, 3, 4],
                                      mode=0)

    # 修改细胞核的类型
    def modify_nuclei(self, event_point):
        point = self.view.mapToScene(event_point)
        if self.cell_contour_ann is not None and self.current_level < 1:
            distance = np.square(np.array([point.x()]) - self.cell_centers_ann[:, 0]) +\
                np.square(np.array([point.y()]) - self.cell_centers_ann[:, 1])
            nearest_idx = np.where(distance == distance.min())
            this_type = self.cell_type_ann[nearest_idx][0]
            this_contour = self.cell_contour_ann[nearest_idx][0]
            # 如果这个细胞之前被修改过则不可再修改
            if this_type not in [0, 1, 2, 3, 4]:
                return
            # 判断点是否在细胞核轮廓内部
            if cv2.pointPolygonTest(this_contour, (int(point.x()), int(point.y())), False) > 0:
                if os.path.exists(os.path.join(constants.cache_path, "AnnotationTypes.json")):
                    with open(os.path.join(constants.cache_path, "AnnotationTypes.json"), 'r') as f:
                        type_dict = json.load(f)
                        f.close()
                else:
                    type_dict = {"背景类别": [166, 84, 2], "表皮细胞": [255, 0, 0], "淋巴细胞": [0, 255, 0],
                                 "基质细胞": [228, 252, 4], "中性粒细胞": [0, 0, 255]}

                # 弹出对话框选择修改类型
                dialog = ChangeAnnotationDiaglog(type_dict, "表皮细胞")
                # 点击确定，修改类别
                if dialog.exec_() == QDialog.Accepted:
                    item = self.view.itemAt(event_point)
                    type_name = dialog.get_text()
                    new_type = dialog.get_idx()
                    this_contour = this_contour.tolist()
                    # 更改细胞核结果文件
                    self.cell_type_ann[nearest_idx] = int(-this_type)
                    # 绘制标注
                    annotation_item, control_point_items, text_item = \
                        self.ToolManager.draw_polygon.draw(this_contour, QColor(*type_dict[type_name]),
                                                       4, self.current_downsample, True)
                    annotation = {"location": this_contour,
                                  "color": type_dict[type_name],
                                  'tool': "多边形",
                                  "type": type_name,
                                  "annotation_item": annotation_item,
                                  'control_point_items': control_point_items,
                                  'text_item': text_item}
                    self.ToolManager.addAnnotation(annotation, self.current_downsample)
                    # 删除绘制的细胞核
                    if hasattr(item, 'category') and hasattr(item, 'is_region'):
                        if item.category == this_type and item.is_region == False:
                            self.scene.removeItem(item)
                return True
        return False

    # 保存修改后的细胞核pkl结果
    def saveNucleiAnn(self, path):
        if self.cell_contour_ann is not None and self.cell_type_ann is not None and self.cell_centers_ann is not None:
            with open(path, 'wb') as f:
                pickle.dump({"type": self.cell_type_ann,
                             "center": self.cell_centers_ann,
                             "contour": self.cell_contour_ann}, f)
                f.close()

    # 设置加载肿瘤微环境分析显示
    def update_microenv_show(self, show_list):
        self.show_list_microenv = show_list
        # 如果当前没有载入结果，则将显示热图，轮廓置为False
        if "显示热图" in show_list:
            if self.heatmap_microenv is not None:
                if self.show_micrienv_colormap_flag:
                    self.show_or_close_heatmap(self.micrienv_colormap, self.heatmap_downsample_microenv, True)
                else:
                    self.show_or_close_heatmap(self.heatmap_microenv, self.heatmap_downsample_microenv, True)
        else:
            self.show_or_close_heatmap(None, None, False)
        self.NucleiContourLoader.last_nuclei = None
        if "显示肿瘤区域轮廓" in show_list:
            if self.tissue_contours_microenv is not None:
                self.show_microenv_region_contour_flag = True
                self.show_or_close_contour(self.tissue_contours_microenv,
                                           self.tissue_colors_microenv,
                                           self.tissue_class_microenv,
                                           self.show_region_types_microenv,)
        else:
            if self.tissue_contours_microenv is not None:
                self.show_microenv_region_contour_flag = False
                self.show_or_close_contour(self.tissue_contours_microenv,
                                           self.tissue_colors_microenv,
                                           self.tissue_class_microenv,
                                           self.show_region_types_microenv,)
        if "显示细胞核轮廓" in show_list:
            if self.cell_contour_microenv is not None:
                self.show_microenv_nuclei_flag = True
                self.show_or_close_nuclei(current_rect=self.get_current_view_scene_rect(),
                                          contours=self.cell_contour_microenv,
                                          centers=self.cell_centers_microenv,
                                          types=self.cell_type_microenv,
                                          color_dict=self.nuclei_type_dict,
                                          show_types=self.show_nuclei_types_microenv)

        else:
            if self.cell_contour_microenv is not None:
                self.show_microenv_nuclei_flag = False
                self.show_or_close_nuclei(current_rect=self.get_current_view_scene_rect(),
                                          contours=self.cell_contour_microenv,
                                          centers=self.cell_centers_microenv,
                                          types=self.cell_type_microenv,
                                          color_dict=self.nuclei_type_dict,
                                          show_types=self.show_nuclei_types_microenv)

    # 设置加载PDL1分析显示
    def update_pdl1_show(self, show_list):
        self.show_list_pdl1 = show_list
        # 如果当前没有载入结果，则将显示热图，轮廓置为False
        if "显示热图" in show_list:
            if self.heatmap_pdl1 is not None:
                self.show_or_close_heatmap(self.heatmap_pdl1, self.heatmap_downsample_pdl1, True)
        else:
            self.show_or_close_heatmap(None, None, False)
        self.NucleiContourLoader.last_nuclei = None
        if "显示肿瘤区域轮廓" in show_list:
            if self.tissue_contours_pdl1 is not None:
                self.show_pdl1_region_contour_flag = True
                self.show_or_close_contour(self.tissue_contours_pdl1,
                                           self.tissue_colors_pdl1,
                                           self.tissue_class_pdl1,
                                           self.show_region_types_pdl1,
                                           Microenv=False)
        else:
            if self.tissue_contours_pdl1 is not None:
                self.show_pdl1_region_contour_flag = False
                self.show_or_close_contour(self.tissue_contours_pdl1,
                                           self.tissue_colors_pdl1,
                                           self.tissue_class_pdl1,
                                           self.show_region_types_pdl1,
                                           Microenv=False)
        if "显示细胞核轮廓" in show_list:
            if self.cell_contour_pdl1 is not None:
                self.show_pdl1_nuclei_flag = True
                self.show_or_close_nuclei(current_rect=self.get_current_view_scene_rect(),
                                          contours=self.cell_contour_pdl1,
                                          centers=self.cell_centers_pdl1,
                                          types=self.cell_type_pdl1,
                                          color_dict=self.nuclei_type_dict,
                                          show_types=self.show_nuclei_types_pdl1,
                                          mode=3)

        else:
            if self.cell_contour_pdl1 is not None:
                self.show_pdl1_nuclei_flag = False
                self.show_or_close_nuclei(current_rect=self.get_current_view_scene_rect(),
                                          contours=self.cell_contour_pdl1,
                                          centers=self.cell_centers_pdl1,
                                          types=self.cell_type_pdl1,
                                          color_dict=self.nuclei_type_dict,
                                          show_types=self.show_nuclei_types_pdl1,
                                          mode=3)


    def update_multimodal_show(self, heatmap, downsample, flag):
        if heatmap is not None:
            self.TileLoader.update_heatmap_background(heatmap, self.heatmap_alpha, downsample)
        self.show_or_close_heatmap(heatmap, downsample, flag)

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

    def closeEvent(self, *args, **kwargs):
        super().closeEvent()
        self.NucleiContourLoader.__del__()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SlideViewer()
    window.show()
    sys.exit(app.exec_())

