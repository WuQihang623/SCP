import sys
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QScrollArea, QApplication, QWidget, QLabel, QSpacerItem, QSizePolicy

from window.utils.FolderSelector import FolderSelector
from window.utils.controller_ComboBox import MulitSeleteComboBox, SigleSeleteCombox


class UI_Controller(QFrame):

    def __init__(self):
        super(UI_Controller, self).__init__()
        self.nucleus_widget = None
        self.nucleus_diff_widget = None
        self.heatmap_widget = None
        self.contour_widget = None
        self.init_UI()

    def init_UI(self):
        self.main_layout = QVBoxLayout(self)

        # 创建一个滚动区域
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        # 创建一个 QWidget 作为滚动区域的内容
        content_widget = QWidget(self)
        content_layout = QVBoxLayout(content_widget)

        self.title_label = QLabel("结果文件目录")
        self.folder_seletector = FolderSelector(False)
        self.nucleus_layout = QVBoxLayout()
        self.nucleus_diff_layout = QVBoxLayout()
        self.heatmap_layout = QVBoxLayout()
        self.contour_layout = QVBoxLayout()
        null = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Expanding)

        content_layout.addWidget(self.title_label)
        content_layout.addWidget(self.folder_seletector)
        content_layout.addLayout(self.nucleus_layout)
        content_layout.addLayout(self.nucleus_diff_layout)
        content_layout.addLayout(self.heatmap_layout)
        content_layout.addLayout(self.contour_layout)
        content_layout.addSpacerItem(null)
        content_layout.setSpacing(15)

        # 设置布局管理器
        content_widget.setLayout(content_layout)
        # 将内容区域设置到滚动区域中
        scroll_area.setWidget(content_widget)
        # 将滚动区域添加到主布局中
        self.main_layout.addWidget(scroll_area)

        # self.add_nucleus_widget({
        #             "肿瘤细胞": {"type": 1, "color": [255, 0, 0], "number": 1000},
        #             "淋巴细胞": {"type": 2, "color": [0, 255, 0], "number": 1000},
        #             "中性粒细胞": {"type": 3, "color": [255, 255, 0], "number": 1000},
        #             "基质细胞": {"type": 4, "color": [0, 0, 255], "number": 1000},
        #         })
        # self.add_contour_widget({
        #             "肿瘤区域": {"color": [255, 0, 0], "type": 1},
        #             "基质区域": {"color": [0, 255, 0], "type": 2},
        #         })
        # self.add_nucleus_diff_widget({
        #             "FN": {"color": [255, 0, 0]},
        #             "FP": {"color": [0, 255, 0]},
        #         })
        # self.add_heatmap_widget({
        #             "heatmap": ["组织区域热力图", "边界区域热力图"],
        #             "downsample": int,
        #         })

    def add_nucleus_widget(self, nucleus_info: dict):
        """
            载入了细胞核分割结果后， 读取了文件中的properties，知道了有哪些类型的细胞，以及细胞的颜色
            生成一个与细胞类型以及颜色一直的选择框
            Args:
                nucleus_info:{
                    "肿瘤细胞": {"type": 1, "color": [255, 0, 0], "number": 1000},
                    "淋巴细胞": {"type": 2, "color": [0, 255, 0], "number": 1000},
                    "中性粒细胞": {"type": 3, "color": [255, 255, 0], "number": 1000},
                    "基质细胞": {"type": 4, "color": [0, 0, 255], "number": 1000},
                }
        """
        if self.nucleus_widget is not None:
            self.removeAllItems(self.nucleus_layout)
            self.nucleus_widget = None
        nucleus_names = []
        nucleus_colors = []
        nucleus_numbers = []
        for name, item in nucleus_info.items():
            nucleus_names.append(name)
            nucleus_colors.append(item["color"])
            nucleus_numbers.append(item["number"])
        label = QLabel("细胞核：")
        self.nucleus_layout.addWidget(label)
        self.nucleus_widget = MulitSeleteComboBox(nucleus_names, nucleus_colors)
        self.nucleus_layout.addWidget(self.nucleus_widget)
        for name, number in zip(nucleus_names, nucleus_numbers):
            label = QLabel(f"{name}的数量：{number}")
            self.nucleus_layout.addWidget(label)

    def add_nucleus_diff_widget(self, nucleus_diff):
        """
            载入了配准的细胞核分割结果后， 读取了文件中的properties，获得FP FN
            Args:
                nucleus_diff: {
                    "FN": {"color": [255, 0, 0]},
                    "FP": {"color": [0, 255, 0]},
                }
        """
        if self.nucleus_diff_widget is not None:
            self.removeAllItems(self.nucleus_diff_layout)
            self.nucleus_diff_widget = None
        diff_name = []
        diff_color = []
        diff_number = []
        for name, item in nucleus_diff.items():
            diff_name.append(name)
            diff_color.append(item["color"])
            diff_number.append(item["number"])
        label = QLabel("对比差异：")
        self.nucleus_diff_layout.addWidget(label)
        self.nucleus_diff_widget = MulitSeleteComboBox(diff_name, diff_color)
        self.nucleus_diff_layout.addWidget(self.nucleus_diff_widget)
        for name, number in zip(diff_name, diff_number):
            label = QLabel(f"{name}的数量：{number}")
            self.nucleus_diff_layout.addWidget(label)


    def add_heatmap_widget(self, heatmap_info: dict):
        """
            载入了热力图结果后， 读取了文件中的properties，知道了有哪些类型的热力图
            生成一个与热力图数量一致的选择框
            Args:
                heatmap_info": {
                    "heatmap": ["组织区域热力图", "边界区域热力图"],
                    "downsample": int,
                }
        """
        if self.heatmap_widget is not None:
            self.removeAllItems(self.heatmap_layout)
            self.heatmap_widget = None
        heatmap_names = []
        for name in heatmap_info["heatmap_info"]:
            heatmap_names.append(name)
        label = QLabel("热力图：")
        self.heatmap_layout.addWidget(label)
        self.heatmap_widget = SigleSeleteCombox(heatmap_names)
        self.heatmap_layout.addWidget(self.heatmap_widget)

    def add_contour_widget(self, contour_info: dict):
        """
            载入了组织区域轮廓结果后， 读取了文件中的properties，知道了有哪些组织的轮廓，以及轮廓的颜色
            Args:
                contour_info： {
                    "肿瘤区域": {"color": [255, 0, 0], "type": 1},
                    "基质区域": {"color": [0, 255, 0], "type": 2},
                }
        """
        if self.contour_widget is not None:
            self.removeAllItems(self.contour_layout)
            self.contour_widget = None
        contour_name = []
        contour_color = []
        for name, item in contour_info.items():
            contour_name.append(name)
            contour_color.append(item["color"])
        label = QLabel("区域轮廓")
        self.contour_layout.addWidget(label)
        self.contour_widget = MulitSeleteComboBox(contour_name, contour_color)
        self.contour_layout.addWidget(self.contour_widget)

    def removeAllItems(self, layout):
        # 从布局中移除所有子项并释放资源
        while layout.count() > 0:
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UI_Controller()
    window.show()
    sys.exit(app.exec_())