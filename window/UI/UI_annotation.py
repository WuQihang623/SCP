import os
import sys
import constants
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor, QPixmap, QIcon
from window.utils.FolderSelector import FolderSelector

class UI_Annotation(QFrame):
    updateChoosedAnnotationSignal = pyqtSignal(int)
    def __init__(self):
        super(UI_Annotation, self).__init__()
        self.init_UI()

        self.annotationTypeDictPath = os.path.join(constants.cache_path, "AnnotationTypes.json")
        self.annotationDir = constants.annotation_path
        os.makedirs(self.annotationDir, exist_ok=True)

        # 信号连接
        self.annotationTree.itemClicked.connect(self.onClickedAnnotationTree)

    def init_UI(self):
        self.main_layout = QVBoxLayout(self)
        self.splitter = QSplitter(Qt.Vertical)

        self.annotationTypeTree = QTreeWidget()
        self.annotationTypeTree.setHeaderLabels(['类别', '颜色'])

        # 设置列宽比例
        header = self.annotationTypeTree.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)

        self.addType_btn = QPushButton("增加类别")
        self.deleteType_btn = QPushButton('删除类别')
        self.type_layout = QGridLayout()
        self.type_layout.addWidget(self.annotationTypeTree, 0, 0, 1, 2)
        self.type_layout.addWidget(self.addType_btn, 1, 0, 1, 1)
        self.type_layout.addWidget(self.deleteType_btn, 1, 1, 1, 1)

        self.annotationTree = QTreeWidget()
        self.annotationTree.setHeaderLabels(['标注名称', '类型', '形状', '颜色', '描述'])
        header = self.annotationTree.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        self.annofolderselector = FolderSelector(mode=1)
        self.label1 = QLabel("标注目录：")
        self.save_btn = QPushButton('保存标注')
        self.loadAnnotation_btn = QPushButton('导入标注')
        self.clearAnnotation_btn = QPushButton('清空标注')
        self.annotaion_layout = QGridLayout()
        self.annotaion_layout.addWidget(self.annotationTree, 0, 0, 1, 3)
        self.annotaion_layout.addWidget(self.label1, 1, 0, 1, 1)
        self.annotaion_layout.addWidget(self.annofolderselector, 1, 1, 1, 2)
        self.annotaion_layout.addWidget(self.save_btn, 2, 1, 1, 1)
        self.annotaion_layout.addWidget(self.loadAnnotation_btn, 2, 0, 1, 1)
        self.annotaion_layout.addWidget(self.clearAnnotation_btn, 2, 2, 1, 1)

        self.label2 = QLabel("待标注切片目录：")
        self.slideFolderSelector = FolderSelector(mode=3)
        self.slideTree = QTreeWidget()
        self.slideTree.setHeaderLabels(["名称", "标注状态"])
        header = self.slideTree.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.slide_layout = QGridLayout()
        self.slide_layout.addWidget(self.label2, 0, 0, 1, 1)
        self.slide_layout.addWidget(self.slideFolderSelector, 0, 1, 1, 1)
        self.load_slide_info_btn = QPushButton("载入待标注切片")
        self.refresh_slide_info_btn = QPushButton("刷新")
        self.slide_layout.addWidget(self.load_slide_info_btn, 1, 0, 1, 1)
        self.slide_layout.addWidget(self.refresh_slide_info_btn, 1, 1, 1, 1)
        self.slide_layout.addWidget(self.slideTree, 2, 0, 1, 2)

        self.type_widget = QWidget()
        self.type_widget.setLayout(self.type_layout)
        self.splitter.addWidget(self.type_widget)
        self.annotation_widget = QWidget()
        self.annotation_widget.setLayout(self.annotaion_layout)
        self.splitter.addWidget(self.annotation_widget)
        self.slide_widget = QWidget()
        self.slide_widget.setLayout(self.slide_layout)
        self.splitter.addWidget(self.slide_widget)
        self.splitter.setSizes([1000, 3000, 1000])
        self.main_layout.addWidget(self.splitter)

        # 设置删除按键
        self.delete_type_action = QAction("删除")
        self.change_type_name_action = QAction("修改标注")
        self.change_type_color_action = QAction("修改颜色")
        self.annotationTypeTree_menu = QMenu()
        self.annotationTypeTree_menu.addAction(self.delete_type_action)
        self.annotationTypeTree_menu.addAction(self.change_type_name_action)
        self.annotationTypeTree_menu.addAction(self.change_type_color_action)

        self.annotationTypeTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.annotationTypeTree.customContextMenuRequested.connect(self.show_annotationTypeTree_menu)

        # 设置修改按钮与删除按钮
        self.modify_annotation_action = QAction("修改标注")
        self.delete_annotation_action = QAction("删除标注")
        self.annotationTree_menu = QMenu()
        self.annotationTree_menu.addAction(self.modify_annotation_action)
        self.annotationTree_menu.addAction(self.delete_annotation_action)

        self.annotationTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.annotationTree.customContextMenuRequested.connect(self.show_annotationTree_menu)

    def setAnnotationTypeDictTreeWidget(self, annotationTypeDict):
        """
            设置annotationTypeTree中的内容
        """
        self.annotationTypeTree.clear()
        for annotation_name, color in annotationTypeDict.items():
            item = QTreeWidgetItem(self.annotationTypeTree)
            pixmap = QPixmap(20, 20)
            color = QColor(*color)
            pixmap.fill(color)
            item.setText(0, annotation_name)
            item.setIcon(1, QIcon(pixmap))

            # 自适应调整宽度
            self.annotationTypeTree.resizeColumnToContents(0)
            self.annotationTypeTree.resizeColumnToContents(1)

    def addItem2AnnotationTreeWidget(self, annotation, annIdx, is_choosed=True, is_switch=False):
        item = QTreeWidgetItem(self.annotationTree)
        item.setText(0, f"标注{annIdx}")
        item.setText(1, annotation['type'])
        item.setText(2, annotation['tool'])
        pixmap = QPixmap(20, 20)
        color = QColor(*annotation['color'])
        pixmap.fill(color)
        item.setIcon(3, QIcon(pixmap))
        description = annotation.get('description')
        if description is not None:
            item.setText(4, description)
        # 让表自适应内容长度
        self.annotationTree.resizeColumnToContents(0)
        self.annotationTree.resizeColumnToContents(1)
        self.annotationTree.resizeColumnToContents(2)
        self.annotationTree.resizeColumnToContents(3)
        self.annotationTree.resizeColumnToContents(4)
        # 设置选中状态
        if is_choosed:
            self.annotationTree.setCurrentItem(item)
        if is_switch:
            self.updateChoosedAnnotationSignal.emit(annIdx)

    def getChoosedAnnotationTypeItem(self):
        """
            获取被点击的AnnotationTypeItem
        """
        item = self.annotationTypeTree.currentItem()
        return item

    def getChoosedAnnotationItem(self):
        item = self.annotationTree.currentItem()
        return item

    def show_annotationTypeTree_menu(self, pos):
        """
            右键，修改标注名称和颜色
        """
        item = self.annotationTypeTree.itemAt(pos)
        if item is not None:
            self.annotationTypeTree_menu.exec_(self.annotationTypeTree.mapToGlobal(pos))

    def show_annotationTree_menu(self, pos):
        """
            右键，删除标注，修改标注
        """
        item = self.annotationTree.itemAt(pos)
        if item is not None:
            self.onClickedAnnotationTree(item)
            self.annotationTree_menu.exec_(self.annotationTree.mapToGlobal(pos))

    def onClickedAnnotationTree(self, item):
        self.annotationTree.setCurrentItem(item)
        choosed_idx = self.annotationTree.indexOfTopLevelItem(item)
        self.updateChoosedAnnotationSignal.emit(choosed_idx)

    def changeAnnotationCategory(self, row, type=None, color=None):
        """
            更改self.annotationTree的显示的标注类别和颜色
            Args:
                row: int
                type: str
                color: QColor
        """
        item = self.annotationTree.topLevelItem(row)
        if type is not None:
            item.setText(1, type)
        if color is not None:
            pixmap = QPixmap(20, 20)
            pixmap.fill(color)
            item.setIcon(3, QIcon(pixmap))

    def set_slide_tree(self, slide_info, slide_dir):
        """
            Args:
                slide_info: 是一个字典，key是文件名, value是标注状态
                slide_dir: 是文件存放路径
        """
        self.slideTree.clear()
        for slide_name, slide_status in slide_info.items():
            slide_path = os.path.join(slide_dir, slide_name)
            if not os.path.exists(slide_path):
                continue
            item = QTreeWidgetItem(self.slideTree)
            item.setText(0, slide_name)
            item.setText(1, slide_status)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = UI_Annotation()
    window.show()
    sys.exit(app.exec_())