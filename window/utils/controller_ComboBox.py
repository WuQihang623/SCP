from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QListWidget, QListWidgetItem, QCheckBox, QVBoxLayout, QLineEdit
from PyQt5.QtGui import QPixmap, QIcon, QColor
from PyQt5.QtCore import pyqtSignal
from functools import partial

class CustomComboBox(QComboBox):
    def __init__(self, items, colors=None):
        super().__init__()

        self.items = items  # 在下拉框中添加全选选项
        self.colors = colors
        self.qCheckBox = []
        self.qLineEdit = QLineEdit()
        self.qLineEdit.setReadOnly(True)
        self.qListWidget = QListWidget()

        for i in range(len(self.items)):
            self.addQCheckBox(i)
            self.qCheckBox[i].stateChanged.connect(partial(self.updateSelectedText, i))

        layout = QVBoxLayout()
        layout.addWidget(self.qLineEdit)
        layout.addWidget(self.qListWidget)
        self.setLayout(layout)

        self.setModel(self.qListWidget.model())
        self.setView(self.qListWidget)
        self.setLineEdit(self.qLineEdit)

    def addQCheckBox(self, i):
        self.qCheckBox.append(QCheckBox())
        self.qCheckBox[i].setText(self.items[i])
        if self.colors is not None:  # 不为全选项添加颜色块
            pixmap = QPixmap(20, 20)
            pixmap.fill(QColor(*self.colors[i]))
            icon = QIcon(pixmap)
            qItem = QListWidgetItem(icon, '', self.qListWidget)
        else:
            qItem = QListWidgetItem(self.qListWidget)

        self.qListWidget.setItemWidget(qItem, self.qCheckBox[i])

    def updateSelectedText(self, checkbox_idx):
        return
class MulitSeleteComboBox(CustomComboBox):
    showItemSignal = pyqtSignal(list)
    def __init__(self, items, colors=None):
        items = ["全选"] + items  # 在下拉框中添加全选选项
        if colors is not None:
            colors = [[0, 0, 0]] + colors
        super().__init__(items, colors)

    def updateSelectedText(self, checkbox_idx):
        if checkbox_idx == 0:
            for i in range(1, len(self.qCheckBox)):
                self.qCheckBox[i].blockSignals(True)
                if self.qCheckBox[0].isChecked():
                    self.qCheckBox[i].setChecked(True)
                else:
                    self.qCheckBox[i].setChecked(False)
                self.qCheckBox[i].blockSignals(False)
        else:
            all_checked = all(self.qCheckBox[i].isChecked() for i in range(1, len(self.qCheckBox)))
            self.qCheckBox[0].blockSignals(True)
            self.qCheckBox[0].setChecked(all_checked)
            self.qCheckBox[0].blockSignals(False)
        selected_items = [self.qCheckBox[i].text() for i in range(1, len(self.qCheckBox)) if self.qCheckBox[i].isChecked()]
        self.qLineEdit.setText(', '.join(selected_items))

        # 发送信号，要显示什么东西
        self.showItemSignal.emit(selected_items)

class SigleSeleteCombox(CustomComboBox):
    showItemSignal = pyqtSignal(list)

    def __init__(self, items, colors=None):
        super().__init__(items, colors)

    def updateSelectedText(self, checkbox_idx):
        # 其他的结果设置为unchecked
        for i in range(0, len(self.qCheckBox)):
            if i!=checkbox_idx:
                self.qCheckBox[i].blockSignals(True)
                self.qCheckBox[i].setChecked(False)
                self.qCheckBox[i].blockSignals(False)
        selected_items = [self.qCheckBox[i].text() for i in range(0, len(self.qCheckBox)) if self.qCheckBox[i].isChecked()]
        self.qLineEdit.setText(', '.join(selected_items))
        # 发送信号，要显示什么东西
        self.showItemSignal.emit(selected_items)


if __name__ == '__main__':
    app = QApplication([])
    items = ["Option 1", "Option 2", "Option 3"]
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]

    window = SigleSeleteCombox(items, colors)
    window.show()
    app.exec_()
