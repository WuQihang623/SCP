import os
import sys
import pickle
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTabWidget, QFileDialog, QMessageBox

from window.UI.UI_annotation import UI_Annotation
from window.UI.UI_Control import UI_Controller

class Controller(QTabWidget):
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

    def setMainViewerName(self, slide_path):
        """
            主窗口的文件名称
        """
        self.mainViewer_name, _ = os.path.splitext(os.path.basename(slide_path))

    def setSideViewerName(self, slide_path):
        """
            副窗口的文件名成
        """
        self.sideViewer_name, _ = os.path.splitext(os.path.basename(slide_path))

    def load_annotation(self):
        """
            载入标注文件
        """
        

    def add_label_category(self):
        """
            增加标注工具的类别，肿瘤区域，基质区域，角化物……
        """

    def remove_label_category(self):
        """
            删除标注类别
            先要获取到当前被选中的标注类别，然后更新标注类别字典
        """

    def change_label_tool(self):
        """
            切换当前的标注工具，切换成： 矩形，多边形，测量工具……
            通过点击标注工具
        """

    def change_label_category(self):
        """
            切换当前标注工具的类型，切换成：肿瘤区域，基质区域……
            通过点击添加的label
        """

    def change_label_color(self):
        """
            更换添加的类别的颜色
            通过双击添加的label
        """

    def change_label_name(self):
        """
            更换添加的类别的名称，
            通过双击添加的label
        """

    def add_annotation(self):
        """
            绘制完成一个标注后，将标注结果记录下来
        """

    def remove_annotation(self):
        """
            删除绘制好的标注
            先获取到被点击的标注，然后删除记录以及场景中的图元
        """

    def modify_annotation(self):
        """
            修改绘制好的标注
            先获取被点击的标注，然后更新标注字典以及场景中的图元
        """

    def save_annotation(self):
        """
            保存标注
        """

    def clear_annotaiton(self):
        """
            清空标注
        """


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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Controller()
    window.show()
    sys.exit(app.exec_())