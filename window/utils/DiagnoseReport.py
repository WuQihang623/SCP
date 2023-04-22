from PyQt5.QtWidgets import (QApplication, QFrame, QVBoxLayout, QLabel, QTextEdit, QComboBox, QLineEdit, QPushButton,
                QSpacerItem, QSizePolicy, QHBoxLayout, QWidget, QCheckBox, QGridLayout, QScrollArea, QMessageBox)
from PyQt5.QtGui import QPixmap, QPainter, QPageSize, QRegion, QPdfWriter, QPagedPaintDevice
import os
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtCore import QSizeF, pyqtSignal, QRectF, QPointF, QPoint, Qt
import glob


class ImageItem(QWidget):
    addPathSignal = pyqtSignal(str)
    def __init__(self, img_path):
        super(ImageItem, self).__init__()
        self.img_path = img_path
        self.label = QLabel()
        pixmap = QPixmap(img_path)
        self.label.setPixmap(pixmap)
        self.checkbox = QCheckBox("选择")
        self.checkbox.toggled.connect(self.add_path)
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.label)
        main_layout.addWidget(self.checkbox)

    def add_path(self):
        self.addPathSignal.emit(self.img_path)

    def cancelAdd(self):
        self.checkbox.blockSignals(True)
        self.checkbox.setChecked(False)
        self.checkbox.blockSignals(False)

class PDF(QFrame):
    def __init__(self,
                 Path_number,
                name,
                gender,
                age,
                outpatient,
                department,
                doctor,
                date,
                admission,
                material,
                diagnose_result,
                describe,
                img_list):
        super(PDF, self).__init__()
        self.init_UI(Path_number,
                     name,
                     gender,
                     age,
                     outpatient,
                     department,
                     doctor,
                     date,
                     admission,
                     material,
                     diagnose_result,
                     describe,
                     img_list)

    def init_UI(self,
                Path_number,
                name,
                gender,
                age,
                outpatient,
                department,
                doctor,
                date,
                admission,
                material,
                diagnose_result,
                describe,
                img_list):
        # self.setFixedSize(1920, 1080)
        main_layout = QVBoxLayout(self)
        title_label = QLabel("病理诊断报告单")
        main_layout.addWidget(title_label)

        Path_number_label = QLabel("病理号：")
        Path_number_text = QLabel(Path_number)
        h_layout1 = QHBoxLayout()
        h_layout1.addWidget(Path_number_label)
        h_layout1.addWidget(Path_number_text)
        main_layout.addLayout(h_layout1)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        h_layout2 = QHBoxLayout()
        name_label = QLabel("姓名：")
        name_text = QLabel(name)
        h_layout2.addWidget(name_label)
        h_layout2.addWidget(name_text)
        spacer1 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout2.addItem(spacer1)

        gender_label = QLabel("性别：")
        gender_text = QLabel(gender)
        h_layout2.addWidget(gender_label)
        h_layout2.addWidget(gender_text)
        spacer2 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout2.addItem(spacer2)

        age_label = QLabel("年龄：")
        age_text = QLabel(age)
        h_layout2.addWidget(age_label)
        h_layout2.addWidget(age_text)
        spacer3 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout2.addItem(spacer3)

        outpatient_label = QLabel("门诊号：")
        outpatient_text = QLabel(outpatient)
        h_layout2.addWidget(outpatient_label)
        h_layout2.addWidget(outpatient_text)
        main_layout.addLayout(h_layout2)

        h_layout3 = QHBoxLayout()
        department_label = QLabel("送检科室：")
        department_text = QLabel(department)
        h_layout3.addWidget(department_label)
        h_layout3.addWidget(department_text)
        spacer4 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout3.addItem(spacer4)

        doctor_label = QLabel("送检医生：")
        doctor_text = QLabel(doctor)
        h_layout3.addWidget(doctor_label)
        h_layout3.addWidget(doctor_text)
        spacer5 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout3.addItem(spacer5)

        date_label = QLabel("送检日期：")
        date_text = QLabel(date)
        h_layout3.addWidget(date_label)
        h_layout3.addWidget(date_text)
        spacer6 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout3.addItem(spacer6)

        admission_label = QLabel("住院号：")
        admission_text = QLabel(admission)
        h_layout3.addWidget(admission_label)
        h_layout3.addWidget(admission_text)
        main_layout.addLayout(h_layout3)

        h_layout4 = QHBoxLayout()
        material_label = QLabel("送检材料：")
        material_text = QLabel(material)
        h_layout4.addWidget(material_label)
        h_layout4.addWidget(material_text)
        spacer7 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout4.addItem(spacer7)

        diagnose_label = QLabel("诊断结论：")
        diagnose_text = QLabel(diagnose_result)
        diagnose_text.setMaximumWidth(80)
        h_layout4.addWidget(diagnose_label)
        h_layout4.addWidget(diagnose_text)
        main_layout.addLayout(h_layout4)

        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line2)

        describe_label = QLabel("描述：")
        describe_text = QLabel(describe)
        describe_text.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        describe_text.setWordWrap(True)
        # describe_text.setFixedWidth(200)
        main_layout.addWidget(describe_label)
        main_layout.addWidget(describe_text)

        grid_layout = QGridLayout()
        cols = 3
        for idx, img_path in enumerate(img_list):
            h = int(idx / cols)
            w = idx % cols
            label = QLabel()
            pixmap = QPixmap(img_path)
            label.setPixmap(pixmap)
            grid_layout.addWidget(label, h, w, 1, 1)
        main_layout.addLayout(grid_layout)

        spacer8 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        main_layout.addItem(spacer8)

class DiagnoseReport(QFrame):
    def __init__(self, img_dir, save_path, diagnose_result):
        super(DiagnoseReport, self).__init__()
        self.init_UI(img_dir, diagnose_result)
        self.save_path = save_path
        self.choosed_path = []
        self.set_style()
        self.setMinimumSize(1500, 800)

    def init_UI(self, img_dir, diagnose_result):
        self.setWindowTitle("诊断报告")
        main_layout = QVBoxLayout(self)
        title_label = QLabel("病理诊断报告单")
        main_layout.addWidget(title_label)

        Path_number_label = QLabel("病理号：")
        self.Path_number_text = QLineEdit()
        self.Path_number_text.setFixedWidth(300)
        h_layout1 = QHBoxLayout()
        h_layout1.addWidget(Path_number_label)
        h_layout1.addWidget(self.Path_number_text)
        spacer0 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout1.addItem(spacer0)
        main_layout.addLayout(h_layout1)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        h_layout2 = QHBoxLayout()
        name_label = QLabel("姓名：")
        self.name_text = QLineEdit()
        self.name_text.setFixedWidth(120)
        h_layout2.addWidget(name_label)
        h_layout2.addWidget(self.name_text)
        spacer1 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout2.addItem(spacer1)

        gender_label = QLabel("性别：")
        self.gender_combox = QComboBox()
        self.gender_combox.addItems(["男", "女"])
        self.gender_combox.setCurrentIndex(1)
        h_layout2.addWidget(gender_label)
        h_layout2.addWidget(self.gender_combox)
        spacer2 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout2.addItem(spacer2)

        age_label = QLabel("年龄：")
        self.age_text = QLineEdit()
        self.age_text.setFixedWidth(80)
        h_layout2.addWidget(age_label)
        h_layout2.addWidget(self.age_text)
        spacer3 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout2.addItem(spacer3)

        outpatient_label = QLabel("门诊号：")
        self.outpatient_text = QLineEdit()
        self.outpatient_text.setFixedWidth(200)
        h_layout2.addWidget(outpatient_label)
        h_layout2.addWidget(self.outpatient_text)
        main_layout.addLayout(h_layout2)

        h_layout3 = QHBoxLayout()
        department_label = QLabel("送检科室：")
        self.department_text = QLineEdit()
        self.department_text.setFixedWidth(200)
        h_layout3.addWidget(department_label)
        h_layout3.addWidget(self.department_text)
        spacer4 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout3.addItem(spacer4)

        doctor_label = QLabel("送检医生：")
        self.doctor_text = QLineEdit()
        self.doctor_text.setFixedWidth(120)
        h_layout3.addWidget(doctor_label)
        h_layout3.addWidget(self.doctor_text)
        spacer5 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout3.addItem(spacer5)

        date_label = QLabel("送检日期：")
        self.date_text = QLineEdit()
        self.date_text.setFixedWidth(150)
        h_layout3.addWidget(date_label)
        h_layout3.addWidget(self.date_text)
        spacer6 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout3.addItem(spacer6)

        admission_label = QLabel("住院号：")
        self.admission_text = QLineEdit()
        self.admission_text.setFixedWidth(200)
        h_layout3.addWidget(admission_label)
        h_layout3.addWidget(self.admission_text)
        main_layout.addLayout(h_layout3)

        h_layout4 = QHBoxLayout()
        material_label = QLabel("送检材料：")
        self.material_text = QLineEdit()
        self.material_text.setFixedWidth(250)
        h_layout4.addWidget(material_label)
        h_layout4.addWidget(self.material_text)
        spacer7 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout4.addItem(spacer7)

        diagnose_label = QLabel("诊断结论：")
        self.diagnose_text = QLineEdit(diagnose_result)
        self.diagnose_text.setMaximumWidth(60)
        h_layout4.addWidget(diagnose_label)
        h_layout4.addWidget(self.diagnose_text)
        main_layout.addLayout(h_layout4)

        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line2)

        describe_label = QLabel("描述：")
        self.describe_text = QTextEdit()
        self.describe_text.setMaximumHeight(120)
        main_layout.addWidget(describe_label)
        main_layout.addWidget(self.describe_text)

        # 创建一个QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        grid_layout = QGridLayout()
        img_paths = glob.glob(os.path.join(img_dir, '*.jpg'))
        cols = 5
        self.imageItems = []
        for idx, img_path in enumerate(img_paths):
            h = int(idx / cols)
            w = idx % cols
            imgItem = ImageItem(img_path)
            self.imageItems.append(imgItem)
            imgItem.addPathSignal.connect(self.update_choosed_path)

            grid_layout.addWidget(imgItem, h, w, 1, 1)

        # 创建一个QWidget，将QGridLayout设置为其布局
        widget = QWidget()
        widget.setLayout(grid_layout)
        # 将QWidget设置为QScrollArea的窗口部件
        scroll.setWidget(widget)
        main_layout.addWidget(scroll)

        save_btn = QPushButton("导出诊断报告")
        save_btn.clicked.connect(self.save)
        main_layout.addWidget(save_btn)

    def update_choosed_path(self, path):
        if path in self.choosed_path:
            self.choosed_path.remove(path)
        else:
            if len(self.choosed_path) > 8:
                for imgItem in self.imageItems:
                    if imgItem.img_path == path:
                        QMessageBox.warning(self, '警告', '至多选择9张图像')
                        imgItem.cancelAdd()
            else:
                self.choosed_path.append(path)

    def export_to_pdf(self, frame):
        # 创建一个QPainter对象
        painter = QPainter()
        # 创建一个QPdfWriter对象
        pdf_writer = QPdfWriter(self.save_path)
        pdf_writer.setPageSize(QPagedPaintDevice.A4)
        pdf_writer.setResolution(100)
        # 将QPainter对象绑定到QPdfWriter对象
        painter.begin(pdf_writer)
        # 渲染QFrame对象
        frame.render(painter)
        # 如果内容过多，新增一页
        while not painter.isActive():
            pdf_writer.newPage()
            frame.render(painter)
        # 结束渲染
        painter.end()

    # 保存诊断报告pdf
    def save(self):
        fram = PDF(self.Path_number_text.text(),
                   self.name_text.text(),
                   self.gender_combox.currentText(),
                   self.age_text.text(),
                   self.outpatient_text.text(),
                   self.department_text.text(),
                   self.doctor_text.text(),
                   self.date_text.text(),
                   self.admission_text.text(),
                   self.material_text.text(),
                   self.diagnose_text.text(),
                   self.describe_text.toPlainText(),
                   self.choosed_path)
        # 保存pdf
        self.export_to_pdf(fram)
        self.close()

    def set_style(self):
        self.setStyleSheet("QLabel { font-size: 22px;}"
                           "QLineEdit {font-size: 20px;}"
                           "QTextEdit {font-size: 20px;}"
                           "QComboBox {font-size: 20px;}"
                           "QPushButton {font-size: 20px;}")


if __name__ == '__main__':
    app = QApplication([])
    window = DiagnoseReport('E:/Program/SCP/results/Diagnose/H1715067/images',
                            'E:/Program/SCP/results/Diagnose/H1715067/report.pdf', "阳性")
    window.show()
    app.exec_()