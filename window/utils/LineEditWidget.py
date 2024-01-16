import json
import sys
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QGridLayout, QApplication, QCheckBox
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import Qt, pyqtSignal

class LineEditWidget(QWidget):
    paramChangedSignal = pyqtSignal(bool, int, int, int)

    def __init__(self, label1_name, label1_value, label2_name, label2_value, path):
        super(LineEditWidget, self).__init__()
        self.path = path
        self.checkbox = QCheckBox("打开参考线")
        self.checkbox.setChecked(False)
        self.checkbox.stateChanged.connect(self.handle_checkbox_state)

        self.label1 = QLabel(label1_name)
        self.line_edit1 = QLineEdit(self)
        self.line_edit1.setText(str(label1_value))
        self.label2 = QLabel(label2_name)
        self.line_edit2 = QLineEdit(self)
        self.line_edit2.setText(str(label2_value))
        self.label3 = QLabel("透明度：")
        self.line_edit3 = QLineEdit(self)
        self.line_edit3.setText(str(70))

        # 设置验证器，只允许输入整数
        validator = QIntValidator(self)
        uint8_validator = QIntValidator(0, 255)
        self.line_edit1.setValidator(validator)
        self.line_edit2.setValidator(validator)
        self.line_edit3.setValidator(uint8_validator)

        # 连接 returnPressed 信号到槽函数
        self.line_edit1.returnPressed.connect(self.handle_return_pressed1)
        self.line_edit2.returnPressed.connect(self.handle_return_pressed1)
        self.line_edit3.returnPressed.connect(self.handle_return_pressed2)

        layout = QGridLayout(self)
        layout.addWidget(self.checkbox, 0, 0, 1, 2)
        layout.addWidget(self.label1, 1, 0, 1, 1)
        layout.addWidget(self.line_edit1, 1, 1, 1, 1)
        layout.addWidget(self.label2, 2, 0, 1, 1)
        layout.addWidget(self.line_edit2, 2, 1, 1, 1)
        layout.addWidget(self.label3, 3, 0, 1, 1)
        layout.addWidget(self.line_edit3, 3, 1, 1, 1)

    def handle_return_pressed1(self):
        value1 = int(self.line_edit1.text())
        value2 = int(self.line_edit2.text())
        value3 = int(self.line_edit3.text())
        with open(self.path, 'w') as f:
            f.write(json.dumps({"patch_size": value1, "stride": value2}))
            f.close()
        print(value1, value2, value3, self.checkbox.isChecked())
        self.paramChangedSignal.emit(self.checkbox.isChecked(), value1, value2, value3)

    def handle_return_pressed2(self):
        value1 = int(self.line_edit1.text())
        value2 = int(self.line_edit2.text())
        value3 = int(self.line_edit3.text())
        print(value1, value2, value3, self.checkbox.isChecked())
        self.paramChangedSignal.emit(self.checkbox.isChecked(), value1, value2, value3)

    def handle_checkbox_state(self, state):
        try:
            value1 = int(self.line_edit1.text())
            value2 = int(self.line_edit2.text())
            value3 = int(self.line_edit3.text())
        except:
            value1 = None
            value2 = None
            value3 = None
        self.paramChangedSignal.emit(self.checkbox.isChecked(), value1, value2, value3)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    my_widget = LineEditWidget("1", 10, "2", 20, "fdas.json")
    my_widget.show()
    sys.exit(app.exec_())
