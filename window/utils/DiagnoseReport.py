from PyQt5.QtWidgets import (QApplication, QFrame, QVBoxLayout, QLabel, QTextEdit, QComboBox, QLineEdit, QPushButton,
                QSpacerItem, QSizePolicy, QHBoxLayout, QWidget, QCheckBox, QGridLayout, QScrollArea, QMessageBox)
from PyQt5.QtGui import QPixmap, QPainter, QPageSize, QRegion, QPdfWriter, QPagedPaintDevice
import os
from PyQt5.QtCore import pyqtSignal, Qt
import glob
import time
from window.utils.PDF import PDF


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


class DiagnoseReport(QFrame):
    def __init__(self, img_dir, save_path, diagnose_result):
        super(DiagnoseReport, self).__init__()
        self.init_UI(img_dir, diagnose_result)
        self.save_path = save_path
        self.choosed_path = []
        self.set_style()
        self.setMinimumSize(1600, 800)

    def init_UI(self, img_dir, diagnose_result):
        self.setWindowTitle("诊断报告")
        main_layout = QVBoxLayout(self)

        hostipal_label = QLabel("南方医科大学珠江医院")
        hostipal_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(hostipal_label)

        title_label = QLabel("病理检查报告单")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        h_layout1= QHBoxLayout()
        patient_ID_label = QLabel("病人ID：")
        self.patient_ID_text = QLineEdit()
        self.patient_ID_text.setFixedWidth(300)
        h_layout1.addWidget(patient_ID_label)
        h_layout1.addWidget(self.patient_ID_text)
        spacer0 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout1.addItem(spacer0)

        admission_label = QLabel("住院号")
        self.admission_text = QLineEdit()
        self.admission_text.setFixedWidth(200)
        h_layout1.addWidget(admission_label)
        h_layout1.addWidget(self.admission_text)
        spacer1 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout1.addItem(spacer1)

        examination_label = QLabel("病检号：")
        self.examination_text = QLineEdit()
        self.examination_text.setFixedWidth(200)
        h_layout1.addWidget(examination_label)
        h_layout1.addWidget(self.examination_text)

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
        spacer2 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout2.addItem(spacer2)

        gender_label = QLabel("性别：")
        self.gender_combox = QComboBox()
        self.gender_combox.addItems(["男", "女"])
        self.gender_combox.setCurrentIndex(1)
        h_layout2.addWidget(gender_label)
        h_layout2.addWidget(self.gender_combox)
        spacer3 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout2.addItem(spacer3)

        age_label = QLabel("年龄：")
        self.age_text = QLineEdit()
        self.age_text.setFixedWidth(80)
        h_layout2.addWidget(age_label)
        h_layout2.addWidget(self.age_text)
        spacer4 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout2.addItem(spacer4)

        check_date_label = QLabel("检查日期：")
        self.check_date_text = QLineEdit()
        self.check_date_text.setFixedWidth(150)
        h_layout2.addWidget(check_date_label)
        h_layout2.addWidget(self.check_date_text)

        h_layout3 = QHBoxLayout()
        department_label = QLabel("申请科室：")
        self.department_text = QLineEdit()
        self.department_text.setFixedWidth(150)
        h_layout3.addWidget(department_label)
        h_layout3.addWidget(self.department_text)
        spacer5 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout3.addItem(spacer5)

        bed_label = QLabel("床号：")
        self.bed_text = QLineEdit()
        self.bed_text.setFixedWidth(120)
        h_layout3.addWidget(bed_label)
        h_layout3.addWidget(self.bed_text)
        spacer6 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout3.addItem(spacer6)

        diagnose_label = QLabel(f"临床诊断：")
        self.diagnose_text = QLineEdit(diagnose_result)
        self.diagnose_text.setFixedWidth(80)
        h_layout3.addWidget(diagnose_label)
        h_layout3.addWidget(self.diagnose_text)

        main_layout.addLayout(h_layout3)

        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line1)

        h_layout4 = QHBoxLayout()

        hostipal_label1 = QLabel("送检医院：南方医科大学珠江医院")
        h_layout4.addWidget(hostipal_label1)
        spacer7 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout4.addItem(spacer7)

        doctor_label = QLabel("申请医生：")
        self.doctor_text = QLineEdit()
        self.doctor_text.setFixedWidth(120)
        h_layout4.addWidget(doctor_label)
        h_layout4.addWidget(self.doctor_text)
        spacer8 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout4.addItem(spacer8)

        material_label = QLabel("送检材料：")
        self.material_text = QLineEdit()
        self.material_text.setFixedWidth(250)
        h_layout4.addWidget(material_label)
        h_layout4.addWidget(self.material_text)
        spacer9 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout4.addItem(spacer9)

        main_layout.addLayout(h_layout4)

        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line2)

        visual_label = QLabel("肉眼检查：")
        self.visual_text = QTextEdit()
        self.visual_text.setMaximumHeight(80)
        main_layout.addWidget(visual_label)
        main_layout.addWidget(self.visual_text)

        microscopic_label = QLabel("镜下检查：")
        self.microscopic_text = QTextEdit()
        self.microscopic_text.setMaximumHeight(80)
        main_layout.addWidget(microscopic_label)
        main_layout.addWidget(self.microscopic_text)

        path_diagnose_label = QLabel("病理诊断：")
        self.path_diagnose_text = QTextEdit()
        self.path_diagnose_text.setMaximumHeight(40)
        main_layout.addWidget(path_diagnose_label)
        main_layout.addWidget(self.path_diagnose_text)

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

        h_layout5 = QHBoxLayout()
        report_date_label = QLabel("报告日期")
        self.report_date_text = QLineEdit(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
        self.report_date_text.setFixedSize(200, 40)
        h_layout5.addWidget(report_date_label)
        h_layout5.addWidget(self.report_date_text)
        spacer8 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout5.addItem(spacer8)

        report_doctor_label = QLabel("报告医师")
        self.report_doctor_text = QLineEdit("")
        self.report_doctor_text.setFixedSize(120, 40)
        h_layout5.addWidget(report_doctor_label)
        h_layout5.addWidget(self.report_doctor_text)
        spacer9 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout5.addItem(spacer9)

        check_doctor_label = QLabel("审核医师：")
        self.check_doctor_text = QLineEdit()
        self.check_doctor_text.setFixedSize(120, 40)
        h_layout5.addWidget(check_doctor_label)
        h_layout5.addWidget(self.check_doctor_text)

        main_layout.addLayout(h_layout5)

        save_btn = QPushButton("导出诊断报告")
        save_btn.clicked.connect(self.save)
        main_layout.addWidget(save_btn)

    def update_choosed_path(self, path):
        if path in self.choosed_path:
            self.choosed_path.remove(path)
        else:
            if len(self.choosed_path) > 3:
                for imgItem in self.imageItems:
                    if imgItem.img_path == path:
                        QMessageBox.warning(self, '警告', '至多选择4张图像')
                        imgItem.cancelAdd()
            else:
                self.choosed_path.append(path)

    def export_to_pdf(self, frame):
        # 创建一个QPainter对象
        painter = QPainter()
        # 创建一个QPdfWriter对象
        pdf_writer = QPdfWriter(self.save_path)
        pdf_writer.setPageSize(QPagedPaintDevice.A4)
        pdf_writer.setResolution(80)

        # 将QPainter对象绑定到QPdfWriter对象
        painter.begin(pdf_writer)

        painter.translate(30, 0)  # 将原点移动到居中位置
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
        fram = PDF(self.patient_ID_text.text(),
                   self.admission_text.text(),
                   self.examination_text.text(),
                   self.name_text.text(),
                   self.gender_combox.currentText(),
                   self.age_text.text(),
                   self.check_date_text.text(),
                   self.department_text.text(),
                   self.bed_text.text(),
                   self.diagnose_text.text(),
                   self.doctor_text.text(),
                   self.material_text.text(),
                   self.visual_text.toPlainText(),
                   self.microscopic_text.toPlainText(),
                   self.path_diagnose_text.toPlainText(),
                   self.choosed_path,
                   self.report_date_text.text(),
                   self.report_doctor_text.text(),
                   self.check_doctor_text.text())
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