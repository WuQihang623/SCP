import json
import os
import re
import sys
import pickle
from enum import Enum
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor, QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTabWidget, QFileDialog, QMessageBox, QDialog

from window.UI.UI_annotation import UI_Annotation
from window.UI.UI_Control import UI_Controller

class AnnotationMode(Enum):
    MOVE = 1
    FIXED_RECT = 2
    RECT = 3
    POLYGON = 4
    MEASURE_TOOL = 5
    MODIFY = 6

class Controller(QTabWidget):
    # 标注
    syncAnnotationSignal = pyqtSignal(dict, int, int) # 是否要将导入的标注
    showAnnotationSignal = pyqtSignal(bool)           # 显示标注
    changeAnnotationItemSignal = pyqtSignal(int, str, list)
    updateChoosedAnnotationSignal = pyqtSignal(int)
    toolChangeSignal = pyqtSignal(int) # 标注工具切换信号
    annotationTypeChooseSignal = pyqtSignal(str, list, int)
    updateAnnotationTypeSignal = pyqtSignal(dict)
    deleteAnnotationSignal = pyqtSignal(int)
    changeAnnotaionSignal = pyqtSignal(int, str, list)

    # 将结果文件传递给Viewer
    mainViewerloadNucleusSignal = pyqtSignal(dict, dict)
    sideViewerloadNucleusSignal = pyqtSignal(dict, dict)
    mainViewerloadheatmapSignal = pyqtSignal(dict, dict)
    sideViewerloadheatmapSignal = pyqtSignal(dict, dict)
    mainViewerloadContourSignal = pyqtSignal(dict, dict)
    sideViewerloadContourSignal = pyqtSignal(dict, dict)
    mainViewerloadNucleusDiffSignal = pyqtSignal(dict, dict)
    sideViewerloadNucleusDiffSignal = pyqtSignal(dict, dict)

    # 将显示信息传递给Viewer
    viewerShowNucleusSignal = pyqtSignal(list, bool)
    viewerShowHeatmapSignal = pyqtSignal(list)
    viewerShowContourSignal = pyqtSignal(list)
    viewerShowNucleusDiffSignal = pyqtSignal(list, bool)

    def __init__(self):
        super().__init__()
        self.annotation_widget = UI_Annotation()
        self.controller_widget = UI_Controller()
        self.addTab(self.annotation_widget, "标注桌面")
        self.addTab(self.controller_widget, "可视化桌面")

        # 初始化变量
        self.mainViewer_name = None
        self.sideViewer_name = None

        # 标注
        self.annotation = {}
        # 被选择上的标注索引
        self.choosedIdx = None
        self.annotationTypeIdx = -1

        # 初始化annotationTypeDict
        self.initAnnotationTypeDictTree()

        self.controllSignalConnections()

    def controllSignalConnections(self):
        """
            控制面板中的信号连接
        """
        self.annotation_widget.addType_btn.clicked.connect(self.add_label_category)
        self.annotation_widget.deleteType_btn.clicked.connect(self.remove_label_category)
        self.annotation_widget.change_type_name_action.triggered.connect(self.change_label_name)
        self.annotation_widget.change_type_color_action.triggered.connect(self.change_label_color)
        self.annotation_widget.delete_type_action.triggered.connect(self.remove_label_category)

        self.annotation_widget.modify_annotation_action.triggered.connect(self.modify_annotation_category)
        self.annotation_widget.delete_annotation_action.triggered.connect(self.remove_annotation_slot)


        self.annotation_widget.loadAnnotation_btn.clicked.connect(self.load_annotation_slot)
        self.annotation_widget.clearAnnotation_btn.clicked.connect(self.clear_annotaiton_slot)
        self.annotation_widget.save_btn.clicked.connect(self.save_annotation_slot)

        self.annotation_widget.updateChoosedAnnotationSignal.connect(self.update_choosed_annotation_slot)

        self.annotation_widget.annotationTypeTree.itemClicked.connect(self.clickedAnnotationTypeTable)

    def setMainViewerName(self, slide_path):
        """
            主窗口的文件名称
        """
        self.mainViewer_name, _ = os.path.splitext(os.path.basename(slide_path))
        self.mainViewer_slidePath = slide_path

    def setSideViewerName(self, slide_path):
        """
            副窗口的文件名成
        """
        self.sideViewer_name, _ = os.path.splitext(os.path.basename(slide_path))

    def initAnnotationTypeDictTree(self):
        if os.path.exists(self.annotation_widget.annotationTypeDictPath):
            with open(self.annotation_widget.annotationTypeDictPath, 'r') as f:
                self.annotationTypeDict = json.load(f)
                f.close()
            if len(self.annotationTypeDict) == 0:
                self.annotationTypeDict = {
                    "肿瘤区域": [255, 0, 0, 255],
                    "基质区域": [0, 0, 255, 255],
                    "其他区域": [142, 255, 111, 255]
                }
        else:
            self.annotationTypeDict = {
                "肿瘤区域": [255, 0, 0, 255],
                "基质区域": [0, 0, 255, 255],
                "其他区域": [142, 255, 111, 255]
            }
        self.annotation_widget.setAnnotationTypeDictTreeWidget(self.annotationTypeDict)

    def load_annotation_slot(self):
        """
            载入标注文件
        """
        options = QFileDialog.Options()
        path, _ = QFileDialog.getOpenFileName(self, "选择标注文件", self.annotation_widget.folderselector.FileDir(),"标注 (*.json)", options=options)
        if not os.path.exists(path):
            return

        # 如果存在标注，则清除掉所有标注
        self.clear_annotaiton_slot()

        with open(path, 'r') as f:
            annotation = json.load(f)
            f.close()

        # 判断标注文件的格式
        if annotation.get("image_path") is None or annotation.get("color_and_type") is None or annotation.get("annotation") is None:
            QMessageBox.warning(self, '警告', '标注文件缺失！')
            return

        # 判断标注文件是否与图像一致
        if self.mainViewer_name not in annotation["image_path"]:
            QMessageBox.warning(self, '警告', '标注与图片不匹配！')
            return

        self.annotationTypeDict = annotation["color_and_type"]

        # 设置标注类别Table
        self.annotation_widget.setAnnotationTypeDictTreeWidget(self.annotationTypeDict)
        self.saveAnnotationTypeDict()

        # 加载标注item Table
        for annIdx, (name, ann) in enumerate(annotation["annotation"].items()):
            self.addAnnotaton(ann, annIdx, is_choosed=False, is_switch=False, sync2ToolManager=True)

        self.showAnnotationSignal.emit(True)


    def addAnnotaton(self, annotation, annIdx, is_choosed=True, is_switch=False, sync2ToolManager=False):
        """
            将标注信息添加到TreeWidget中，并显示到viewer中
            Args:
                annotation: 标注信息
                annIdx: 标注的索引
                is_choosed: 是否选中该标注
                sync2ToolManager: 是否要将annotation传递给ToolManager
        """
        self.annotation[f"标注{annIdx}"] = annotation
        self.annotation_widget.addItem2AnnotationTreeWidget(annotation, annIdx, is_choosed, is_switch)
        if sync2ToolManager:
            self.syncAnnotationSignal.emit(annotation, annIdx ,annIdx if is_choosed else -1)

    def update_choosed_annotation_slot(self, annIdx):
        self.choosedIdx = annIdx
        self.updateChoosedAnnotationSignal.emit(annIdx)

    def saveAnnotationTypeDict(self):
        """
            保存标注的类别文件
        """
        self.updateAnnotationTypeSignal.emit(self.annotationTypeDict)
        with open(self.annotation_widget.annotationTypeDictPath, 'w') as f:
            f.write(json.dumps(self.annotationTypeDict, indent=2))
            f.close()
        return

    def add_label_category(self):
        """
            增加标注工具的类别，肿瘤区域，基质区域，角化物……
        """
        from window.dialog.colorChoosedDialog import ColorChooseDialog
        dialog = ColorChooseDialog()
        if dialog.exec_() == QDialog.Rejected:
            return
        text = dialog.get_text()
        color = dialog.get_color()
        if text ==  "" or not isinstance(color, QColor):
            return
        if text in self.annotationTypeDict.keys() or list(color.getRgb()) in self.annotationTypeDict.values():
            QMessageBox.warning(self, '警告', "该颜色或文本已被添加！")
            return
        self.annotationTypeDict[text] = list(color.getRgb())
        self.annotation_widget.setAnnotationTypeDictTreeWidget(self.annotationTypeDict)
        self.saveAnnotationTypeDict()

        # TODO: 绑定颜色块

    def remove_label_category(self):
        """
            删除标注类别
            先要获取到当前被选中的标注类别，然后更新标注类别字典
        """
        item = self.annotation_widget.getChoosedAnnotationTypeItem()
        if item is None:
            return

        # 查看当前标注中是否存在要删除的类别
        existed_type = [annotation['type'] for name, annotation in self.annotation.items()]

        if item.text(0) in existed_type:
            QMessageBox.warning(self, '警告', '无法删除已存在的标注类型！')
            return
        self.annotationTypeDict.pop(item.text(0))
        self.annotation_widget.setAnnotationTypeDictTreeWidget(self.annotationTypeDict)
        self.saveAnnotationTypeDict()

        # TODO: 绑定颜色块

    def change_label_name(self):
        """
            更换添加的类别的名称，
            通过双击添加的label
        """
        item = self.annotation_widget.getChoosedAnnotationTypeItem()
        if item is None:
            return
        item_type = item.text(0)
        color = self.annotationTypeDict[item_type]

        from window.dialog.ChangeTypeDialog import ChangeTypeDialog
        dialog = ChangeTypeDialog()
        if dialog.exec_() == QDialog.Rejected:
            return
        new_type = dialog.get_text()
        if new_type == "" or new_type in self.annotationTypeDict.keys():
            QMessageBox.warning(self, "警告", "修改类别不成功")
            return

        item.setText(0, new_type)

        from function import update_dict_key
        self.annotationTypeDict = update_dict_key(self.annotationTypeDict, item_type, new_type)
        self.saveAnnotationTypeDict()

        # 更新self.annotation中的结果，annotation_widget中的结果，以及viewer中的可视化
        for annIdx, (name, annItem) in enumerate(self.annotation.items()):
            if annItem["type"] != item_type:
                continue
            self.annotation["name"]["type"] = new_type
            self.annotation_widget.changeAnnotationCategory(annIdx, new_type)
            self.changeAnnotationItemSignal.emit(annIdx, new_type, color)

    def change_label_color(self):
        """
            更换添加的类别的颜色
            通过双击添加的label
        """
        item = self.annotation_widget.getChoosedAnnotationTypeItem()
        if item is None:
            return

        from PyQt5.QtWidgets import QColorDialog
        new_color = QColorDialog.getColor(QColor(0, 0, 0), self, "选择颜色")
        if not new_color.isValid():
            return

        # 判断是否与之前的颜色一致
        if list(new_color.getRgb()) in self.annotationTypeDict.values():
            QMessageBox.warning(self, "警告", "颜色已经存在！")
            return

        current_type = item.text(0)

        self.annotationTypeDict[current_type] = list(new_color.getRgb())
        self.annotation_widget.setAnnotationTypeDictTreeWidget(self.annotationTypeDict)
        self.saveAnnotationTypeDict()

        # 更新self.annotation中的结果，annotation_widget中的结果，以及viewer中的可视化
        for annIdx, (name, annItem) in enumerate(self.annotation.items()):
            if annItem["type"] != current_type:
                continue
            self.annotation["name"]["color"] = list(new_color.getRgb())
            self.annotation_widget.changeAnnotationCategory(annIdx, None, new_color)
            self.changeAnnotationItemSignal.emit(annIdx, current_type, list(new_color.getRgb()))

    def clickedAnnotationTypeTable(self, item, colum):
        row = self.annotation_widget.annotationTypeTree.indexOfTopLevelItem(item)
        self.switch_label_category(row)

    def switch_label_category(self, annTypeIdx):
        """
            切换当前标注工具的类型，切换成：肿瘤区域，基质区域……
            通过点击添加的label
        """
        numTypes = self.annotation_widget.annotationTypeTree.topLevelItemCount()
        if annTypeIdx >= numTypes or annTypeIdx < 0:
            return
        self.annotationTypeIdx = annTypeIdx
        label_category = self.annotation_widget.annotationTypeTree.topLevelItem(annTypeIdx).text(0)
        label_color = self.annotationTypeDict[label_category]
        self.annotationTypeChooseSignal.emit(label_category, label_color, annTypeIdx)

    def change_label_tool(self, mode):
        """
            切换当前的标注工具，切换成： 矩形，多边形，测量工具……
            通过点击标注工具
        """
        self.toolChangeSignal.emit(mode)

    def remove_annotation_slot(self):
        """
            删除绘制好的标注
            先获取到被点击的标注，然后删除记录以及场景中的图元
        """
        item = self.annotation_widget.getChoosedAnnotationItem()
        if item is None:
            return
        row_idx = self.annotation_widget.annotationTree.indexOfTopLevelItem(item)

        from window.dialog.AffirmDialog import AffirmDialog
        from function.delDictItem import delDictItem

        dialog = AffirmDialog("是否要删除该标注？")
        if dialog.exec_() == QDialog.Rejected:
            return

        self.annotation_widget.annotationTree.clearSelection()
        self.choosedIdx = None
        self.annotation = delDictItem(self.annotation, row_idx)

        item_to_remove = self.annotation_widget.annotationTree.topLevelItem(row_idx)
        self.annotation_widget.annotationTree.takeTopLevelItem(self.annotation_widget.annotationTree.indexOfTopLevelItem(item_to_remove))

        # 遍历修改每一行
        for i in range(self.annotation_widget.annotationTree.topLevelItemCount()):
            item = self.annotation_widget.annotationTree.topLevelItem(i)
            name = item.text(0)
            old_idx = int(re.search(r'\d+', name).group())
            if old_idx > row_idx:
                item.setText(0, f"标注{old_idx - 1}")

        # 将idx发送给ToolManager，并对key进行重命名
        self.deleteAnnotationSignal.emit(row_idx)

    def modify_annotation_slot(self, annotation, choosed_idx):
        """
            修改绘制好的标注
            先获取被点击的标注，然后更新标注字典
        """
        self.annotation[f"标注{choosed_idx}"] = annotation

    def modify_annotation_category(self):
        """
            修改标注的类别和颜色
        """
        item = self.annotation_widget.getChoosedAnnotationItem()
        if item is None:
            return

        from window.dialog.changeAnnotationDialog import ChangeAnnotationDiaglog
        row_idx = self.annotation_widget.annotationTree.indexOfTopLevelItem(item)
        old_type = item.text(0)
        dialog = ChangeAnnotationDiaglog(self.annotationTypeDict, old_type)
        if dialog.exec_() == QDialog.Rejected:
            return
        new_type = dialog.get_text()
        new_color = self.annotationTypeDict[new_type]

        if old_type == new_type:
            return

        self.annotation[f'标注{row_idx}']['type'] = new_type
        self.annotation[f"标注{row_idx}"]['color'] = new_color
        item.setText(1, new_type)
        pixmap = QPixmap(20, 20)
        color = QColor(*new_color)
        pixmap.fill(color)
        item.setIcon(3, QIcon(pixmap))

        self.changeAnnotaionSignal.emit(row_idx, new_type, new_color)

    def save_annotation_slot(self):
        """
            保存标注
        """
        if len(self.annotation) <= 0 :
            return
        options = QFileDialog.Options()
        path, _ = QFileDialog.getSaveFileName(self, '保存标注',
                                              f'{self.annotation_widget.annotationDir}/{self.mainViewer_name}_annotation.json', 'json Files(*.json)', options=options)
        if path == "":
            return
        from function.check_write_permission import check_write_permission
        permission = check_write_permission(os.path.dirname(path))
        if permission is False:
            QMessageBox.warning(self, "警告", "该文件夹没有写权限！")
            return
        annotation = {"image_path": self.mainViewer_slidePath,
                      "color_and_type": self.annotationTypeDict,
                      "annotation": self.annotation}
        with open(path, 'w') as f:
            f.write(json.dumps(annotation, indent=2, ensure_ascii=False))
            f.close()

    def clear_annotaiton_slot(self):
        """
            清空标注
        """
        if self.annotation is None or len(self.annotation) == 0:
            return

        from window.dialog.AffirmDialog import AffirmDialog
        dialog = AffirmDialog("是否要保存当前的标注？")
        if dialog.exec_() == QDialog.Accepted:
            self.save_annotation_slot()

        # TODO: 发送信号，清空mainViewer中的标注
        rows = self.annotation_widget.annotationTree.topLevelItemCount()
        self.choosedIdx = None
        for row in range(rows-1, -1, -1):
            self.deleteAnnotationSignal.emit(row)
        self.annotation = {}
        self.annotation_widget.annotationTree.clear()

    """
        结果文件的格式
        Args: {
            "properties": {
                "nucleus_info": {
                    "肿瘤细胞": {"type": 1, "color": [255, 0, 0], "number": 1000},
                    "淋巴细胞": {"type": 2, "color": [0, 255, 0], "number": 1000},
                    "中性粒细胞": {"type": 3, "color": [255, 255, 0], "number": 1000},
                    "基质细胞": {"type": 4, "color": [0, 0, 255], "number": 1000},
                },
                "nucleus_diff_info": {
                    "FN": {"color": [255, 0, 0]},
                    "FP": {"color": [0, 255, 0]},
                }
                "heatmap_info": {
                    "heatmap": ["组织区域热力图", "边界区域热力图"],
                    "downsample": int,
                },
                "contour_info": {
                    "肿瘤区域": {"color": [255, 0, 0], "type": 1},
                    "基质区域": {"color": [0, 255, 0], "type": 2},
                    "图像块": {"color": [0, 0, 0], "type": 3}
                }
            }
            "nucleus_info": {
                "type": ndarray,
                "center": ndarray,
                "contour": ndarray,
            },
            "nucleus_diff_info": {
                "center": ndarray,
                "diff_array": ndarray = ["TP", "TN", "FP", "FN", ...]
            },
            "heatmap_info": {
                "组织区域热力图": ndarray,
                "边界区域热力图": ndarray,
            }
            "contour_info": {
                "contour": ndarray,  array[array(contour1), array(contour2), ...]
                "type": ndarray, array[1, 2, 3, ...]
            }
            
        }
    """
    def load_nucleus_signal_fn(self, main_viewer: bool=True):
        """
            载入细胞核结果文件
            Args:
                main_viewer: 是否为主窗口，或者是对比窗口
        """
        path = self.selete_path(main_viewer, "选择细胞核分割结果")
        if path is None or path == "":
            return
        with open(path, 'rb') as f:
            data = pickle.load(f)
            f.close()

        # 检查文件是否正确
        properties = data.get("properties", {}).get("nucleus_info")
        nucleus_info = data.get("nucleus_info")
        if properties is None or nucleus_info is None:
            QMessageBox.warning(self, '警告', "细胞核分割结果不存在于该文件中")
            return

        for _, item in properties.items():
            if item.get("color") is None or item.get("type") is None:
                QMessageBox.warning(self, '警告', "细胞核分割结果有误")
                return
        try:
            if nucleus_info["center"].shape[0] != nucleus_info["type"].shape[0] or nucleus_info["center"].shape[0] != nucleus_info["contour"].shape[0]:
                QMessageBox.warning(self, '警告', "细胞核分割结果有误")
                return
        except:
            QMessageBox.warning(self, '警告', "细胞核分割结果有误")
            return

        # 计算各种细胞核的数量
        for nucleus_name, item in properties.items():
            properties[nucleus_name]["number"] = int((nucleus_info["type"] == item["type"]).sum())

        self.controller_widget.add_nucleus_widget(properties)
        self.controller_widget.nucleus_widget.showItemSignal.connect(self.show_nucleus_signal_fn)
        if main_viewer:
            self.mainViewerloadNucleusSignal.emit(properties, nucleus_info)
        else:
            self.sideViewerloadNucleusSignal.emit(properties, nucleus_info)
        self.controller_widget.nucleus_widget.chooseFirst()

    def show_nucleus_signal_fn(self, show_nucleus: list):
        """
            显示/关闭细胞核分割结果
            选择要显示哪些细胞核
        """
        self.viewerShowNucleusSignal.emit(show_nucleus, True)

    def load_heatmap_signal_fn(self, main_viewer:bool = True):
        """
            载入热力图
            Args:
                main_viewer: 是否为主窗口，或者是对比窗口
        """
        path = self.selete_path(main_viewer, "选择热力图结果")
        if path is None or path == "":
            return
        with open(path, 'rb') as f:
            data = pickle.load(f)
            f.close()

        properties = data.get("properties", {}).get("heatmap_info")
        heatmap_info = data.get("heatmap_info")
        if properties is None or heatmap_info is None:
            QMessageBox.warning(self, '警告', "热力图结果不存在于该文件中")
            return

        if not isinstance(properties.get("downsample"), int):
            QMessageBox.warning(self, '警告', "properties中的downsample应为一个int类型的值")
            return

        if len(properties["heatmap_info"]) != len(heatmap_info):
            QMessageBox.warning(self, '警告', "properties 与 结果对应不上")
            return

        self.controller_widget.add_heatmap_widget(properties)
        self.controller_widget.heatmap_widget.showItemSignal.connect(self.show_heatmap_signal_fn)
        if main_viewer:
            self.mainViewerloadheatmapSignal.emit(properties, heatmap_info)
        else:
            self.sideViewerloadheatmapSignal.emit(properties, heatmap_info)
        self.controller_widget.heatmap_widget.chooseFirst()

    def show_heatmap_signal_fn(self, showItem: list):
        """
            显示/关闭热力图
            选择要显示哪些热力图
        """
        self.viewerShowHeatmapSignal.emit(showItem)

    def load_contour_signal_fn(self, main_viewer):
        """
            载入轮廓文件
            选择要显示哪些轮廓
            Args:
                main_viewer: 是否为主窗口，或者是对比窗口
        """
        path = self.selete_path(main_viewer, "选择区域轮廓结果")
        if path is None or path == "":
            return
        with open(path, 'rb') as f:
            data = pickle.load(f)
            f.close()

        properties = data.get("properties", {}).get("contour_info")
        contour_info = data.get("contour_info")
        if properties is None or contour_info is None:
            QMessageBox.warning(self, '警告', "区域轮廓结果不存在于该文件中")
            return

        for name, item in properties.items():
            if item.get("type") is None or item.get("color") is None:
                QMessageBox.warning(self, '警告', "properties 文件缺失")
                return
        try:
            if contour_info["contour"].shape[0] != contour_info["type"].shape[0]:
                QMessageBox.warning(self, '警告', "区域轮廓结果错误")
                return
        except:
            QMessageBox.warning(self, '警告', "区域轮廓结果错误")
            return

        self.controller_widget.add_contour_widget(properties)
        self.controller_widget.contour_widget.showItemSignal.connect(self.show_contour_signal_fn)
        if main_viewer:
            self.mainViewerloadContourSignal.emit(properties, contour_info)
        else:
            self.sideViewerloadContourSignal.emit(properties, contour_info)
        self.controller_widget.contour_widget.chooseFirst()

    def show_contour_signal_fn(self, showItem: list):
        """
            显示/关闭轮廓
            选择要显示哪些类型的轮廓
        """
        self.viewerShowContourSignal.emit(showItem)

    def load_nucleus_diff_signal_fn(self, main_viewer:bool = True):
        """
            载入差异文件
            Args:
                main_viewer: 是否为主窗口，或者是对比窗口
        """
        path = self.selete_path(main_viewer, "选择细胞核差异结果")
        if path is None or path == "":
            return
        with open(path, 'rb') as f:
            data = pickle.load(f)
            f.close()
        properties = data.get("properties", {}).get("nucleus_diff_info")
        nucleus_diff_info = data.get("nucleus_diff_info")
        if properties is None or nucleus_diff_info is None:
            QMessageBox.warning(self, '警告', "细胞核差异结果不存在于该文件中")
            return

        for name, item in properties.items():
            if item.get("color") is None:
                QMessageBox.warning(self, '警告', "properties 文件缺失！")
                return
        try:
            if nucleus_diff_info["center"].shape[0] != nucleus_diff_info["diff_array"].shape[0]:
                QMessageBox.warning(self, '警告', "细胞核差异结果缺失！")
                return
        except:
            QMessageBox.warning(self, '警告', "细胞核差异结果缺失！")
            return

        for name, item in properties.items():
            properties[name]["number"] = int((nucleus_diff_info["diff_array"]==name).sum())

        self.controller_widget.add_nucleus_diff_widget(properties)
        self.controller_widget.nucleus_diff_widget.showItemSignal.connect(self.show_nucleus_diff_signal_fn)
        if main_viewer:
            self.mainViewerloadNucleusDiffSignal.emit(properties, nucleus_diff_info)
        else:
            self.sideViewerloadNucleusDiffSignal.emit(properties, nucleus_diff_info)
        self.controller_widget.nucleus_diff_widget.chooseFirst()

    def show_nucleus_diff_signal_fn(self, showItem: list):
        """
            显示/关闭差异点
        """
        self.viewerShowNucleusDiffSignal.emit(showItem, True)

    def selete_path(self, mainViewer:bool, title):
        """
            打开窗口用于选择结果文件
            Args:
                mainViewer: 是否为主窗口
                title: window title
        """
        file_dir = self.controller_widget.folder_seletector.FileDir()
        if not os.path.isdir(file_dir):
            file_dir = "./"
        options = QFileDialog.Options()
        path, _ = QFileDialog.getOpenFileName(self, title, file_dir, "结果(*.pkl)", options=options)
        if path == "":
            return None
        if mainViewer:
            slide_name = self.mainViewer_name
        else:
            slide_name = self.sideViewer_name
        if slide_name not in path:
            QMessageBox.warning(self, '警告', '结果文件与图片不匹配！')
            return None
        return path

    def closeEvent(self, event):
        super().closeEvent(event)
        del self.annotation
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Controller()
    window.show()
    sys.exit(app.exec_())