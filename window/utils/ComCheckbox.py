import time

from PyQt5.QtWidgets import QComboBox, QLineEdit, QListWidget, QCheckBox, QListWidgetItem
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap, QColor, QIcon

class ComboCheckBox(QComboBox):
    selectionChangedSignal = pyqtSignal(list)
    def __init__(self, items, colors=None):
        super(ComboCheckBox, self).__init__()
        self.items = items
        self.colors = colors
        # 下拉框
        self.qCheckBox = []
        # 文本框
        self.qLineEdit = QLineEdit()
        self.qLineEdit.setReadOnly(True)
        self.qListWidget = QListWidget()
        for i in range(len(self.items)):
            self.addQCheckBox(i)
            self.qCheckBox[i].setCheckable(False)
            self.qCheckBox[i].stateChanged.connect(self.show1)
        self.setModel(self.qListWidget.model())
        self.setView(self.qListWidget)
        self.setLineEdit(self.qLineEdit)

    # 添加下拉框的item
    def addQCheckBox(self, i):
        self.qCheckBox.append(QCheckBox())
        self.qCheckBox[i].setText(self.items[i])
        if self.colors is not None:
            pixmap = QPixmap(20, 20)
            pixmap.fill(QColor(*self.colors[i]))
            icon = QIcon(pixmap)
            qItem = QListWidgetItem(icon, '', self.qListWidget)
        else:
            qItem = QListWidgetItem(self.qListWidget)
        self.qListWidget.setItemWidget(qItem, self.qCheckBox[i])

    # 函数用于获取所有选中的复选框，并返回一个列表
    def Selectlist(self):
        Outputlist = []
        for i in range(len(self.qCheckBox)):
            if self.qCheckBox[i].isChecked() == True:
                Outputlist.append(self.qCheckBox[i].text())
                self.qCheckBox[i].stateChanged.connect(self.show)
        print(Outputlist)
        self.Selectedrow_num = len(Outputlist)
        return Outputlist

    # 用于在qLineEdit中显示所选内容的文本，并根据所选项目的数量更新qCheckBox的状态。
    def show1(self):
        show = ''
        Outputlist = self.Selectlist()
        self.qLineEdit.setReadOnly(False)
        self.qLineEdit.clear()
        for i in Outputlist:
            show += i + ';'
        self.qLineEdit.setText(show)
        self.qLineEdit.setReadOnly(True)
        self.selectionChangedSignal.emit(Outputlist)

    # 设置哪些item被选中
    def setChecked(self, idxs):
        for qcheckbox in self.qCheckBox:
            qcheckbox.setCheckable(True)
        for idx in range(len(self.qCheckBox)):
            if idx not in idxs:
                self.qCheckBox[idx].setChecked(False)
            else:
                self.qCheckBox[idx].setChecked(True)

    def clear(self):
        for i in range(len(self.qCheckBox)):
            self.qCheckBox[i].setChecked(False)