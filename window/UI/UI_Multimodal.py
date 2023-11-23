import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from window.utils.FolderSelector import FolderSelector

class ModalCheck(QWidget):
    modalcheckSignal = pyqtSignal(object)
    def __init__(self, modals):
        super().__init__()
        self.initUI(modals)

    def initUI(self, modals: list):
        self.layout = QVBoxLayout(self)
        self.checkbox_list = []
        for modal_name in modals:
            checkbox = QCheckBox(modal_name, self)
            checkbox.toggled.connect(self.checkboxClicked)
            self.layout.addWidget(checkbox)
            self.checkbox_list.append(checkbox)

        # 记录上一次被选中的复选框的索引
        self.last_checked_index = None
        # self.show()

    def checkboxClicked(self):
        # 获取被选中的复选框的索引
        checked_indices = [i for i, checkbox in enumerate(self.checkbox_list) if checkbox.isChecked()]
        # 如果有多个复选框被选中，取消上一次的选中状态
        if len(checked_indices) > 1:
            for indice in checked_indices:
                if indice == self.last_checked_index:
                    self.checkbox_list[indice].blockSignals(True)
                    self.checkbox_list[indice].setChecked(False)
                    self.checkbox_list[indice].blockSignals(False)
        checked_indices = [i for i, checkbox in enumerate(self.checkbox_list) if checkbox.isChecked()]
        if len(checked_indices) == 0: self.last_checked_index = None
        else: self.last_checked_index = checked_indices[0]
        self.modalcheckSignal.emit(self.last_checked_index)
        print(self.last_checked_index)


class UI_Multimodal(QWidget):
    def __init__(self):
        super(UI_Multimodal, self).__init__()
        self.init_UI()

    def init_UI(self):
        self.mainlayout = QVBoxLayout(self)
        WidgetBox = QGroupBox()
        WidgetBox.setTitle('多模态可视化')
        self.btn_layout = QGridLayout()
        self.btn_layout.setVerticalSpacing(25)
        self.btn_layout.setHorizontalSpacing(20)
        self.wsi_path_text = QLabel()
        self.wsi_path_text.setWordWrap(True)
        self.folderselector = FolderSelector()
        self.load_btn = QPushButton("载入结果")
        self.load_comparison_btn = QPushButton("载入对比结果")
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.btn_layout.addWidget(self.folderselector, 1, 0, 1, 1)
        self.btn_layout.addWidget(self.load_btn, 2, 0, 1, 1)
        self.btn_layout.addWidget(self.load_comparison_btn, 3, 0, 1, 1)
        self.btn_layout.addWidget(line, 4, 0, 1, 1)
        null = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.btn_layout.addItem(null, 6, 0, 1, 1)
        WidgetBox.setLayout(self.btn_layout)
        self.mainlayout.addWidget(WidgetBox)
        self.modal_check = None

    def load_checkbox(self, modal_list):
        self.clear_colorbar()
        self.modal_check = ModalCheck(modal_list)
        self.modal_check.modalcheckSignal.connect(self.changeHeatmap)
        self.btn_layout.addWidget(self.modal_check, 5, 0, 1, 1)

    def clear_colorbar(self):
        if self.modal_check is not None:
            self.btn_layout.removeWidget(self.modal_check)
            self.modal_check.setParent(None)
            self.modal_check.deleteLater()
            self.modal_check = None

    def changeHeatmap(self, index):
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # app.setStyleSheet(qdarkstyle.load_stylesheet())
    window = UI_Multimodal()
    window.show()
    sys.exit(app.exec_())
