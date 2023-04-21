import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

class UI_Annotation(QFrame):
    def __init__(self):
        super(UI_Annotation, self).__init__()
        self.init_UI()

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
        self.changeType_btn = QPushButton('修改类别')
        self.type_layout = QGridLayout()
        self.type_layout.addWidget(self.annotationTypeTree, 0, 0, 1, 2)
        self.type_layout.addWidget(self.addType_btn, 1, 0, 1, 1)
        self.type_layout.addWidget(self.changeType_btn, 1, 1, 1, 1)

        self.annotationTree = QTreeWidget()
        self.annotationTree.setHeaderLabels(['标注名称', '类型', '形状', '颜色'])
        self.save_btn = QPushButton('保存标注')
        self.loadAnnotation_btn = QPushButton('导入标注')
        self.clearAnnotation_btn = QPushButton('清空标注')
        self.annotaion_layout = QGridLayout()
        self.annotaion_layout.addWidget(self.annotationTree, 0, 0, 1, 3)
        self.annotaion_layout.addWidget(self.save_btn, 1, 1, 1, 1)
        self.annotaion_layout.addWidget(self.loadAnnotation_btn, 1, 0, 1, 1)
        self.annotaion_layout.addWidget(self.clearAnnotation_btn, 1, 2, 1, 1)

        self.type_widget = QWidget()
        self.type_widget.setLayout(self.type_layout)
        self.splitter.addWidget(self.type_widget)
        self.annotation_widget = QWidget()
        self.annotation_widget.setLayout(self.annotaion_layout)
        self.splitter.addWidget(self.annotation_widget)
        self.splitter.setSizes([1000, 2000])
        self.main_layout.addWidget(self.splitter)

        # 设置annotationTypeTree的列宽策略
        # header = self.annotationTypeTree.header()
        # header.setSectionResizeMode(0, header.Stretch)
        # header.setSectionResizeMode(1, header.Stretch)

        # header = self.annotationTree.header()
        # header.setSectionResizeMode(0, header.Stretch)
        # header.setSectionResizeMode(1, header.Stretch)
        # header.setSectionResizeMode(2, header.Stretch)
        # header.setSectionResizeMode(3, header.Stretch)

        # 设置删除按键
        self.delete_type_action = QAction("删除")
        self.delete_type_action.triggered.connect(self.delete_annotationTypeItem)
        self.annotationTypeTree_menu = QMenu()
        self.annotationTypeTree_menu.addAction(self.delete_type_action)

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


    def show_annotationTypeTree_menu(self, pos):
        item = self.annotationTypeTree.itemAt(pos)
        if item is not None:
            self.annotationTypeTree_menu.exec_(self.annotationTypeTree.mapToGlobal(pos))

    def delete_annotationTypeItem(self):
        items = self.annotationTypeTree.selectedItems()
        for item in items:
            (item.parent() or self.annotationTypeTree.invisibleRootItem()).removeChild(item)

    def show_annotationTree_menu(self, pos):
        item = self.annotationTree.itemAt(pos)
        if item is not None:
            self.annotationTree_menu.exec_(self.annotationTree.mapToGlobal(pos))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = UI_Annotation()
    window.show()
    sys.exit(app.exec_())