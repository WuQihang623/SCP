from PyQt5.QtWidgets import (QApplication, QFrame, QVBoxLayout, QLabel, QTextEdit, QComboBox, QLineEdit, QPushButton,
                QSpacerItem, QSizePolicy, QHBoxLayout, QWidget, QCheckBox, QGridLayout, QScrollArea, QMessageBox)
from PyQt5.QtGui import QPixmap, QPainter, QPageSize, QRegion, QPdfWriter, QPagedPaintDevice
import os
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtCore import QSizeF, pyqtSignal, QRectF, QPointF, QPoint, Qt
import glob
import time



class PDF(QFrame):
    def __init__(self,
                 patient_ID,
                 admission,
                 examination,
                 name,
                 gender,
                 age,
                 check_date,
                 department,
                 bed,
                 diagnose_result,
                 doctor,
                 material,
                 visual,
                 microscopic,
                 path_diagnose,
                 img_list,
                 report_date,
                 report_doctor,
                 check_doctor
                 ):
        super(PDF, self).__init__()
        self.init_UI(
            patient_ID,
            admission,
            examination,
            name,
            gender,
            age,
            check_date,
            department,
            bed,
            diagnose_result,
            doctor,
            material,
            visual,
            microscopic,
            path_diagnose,
            img_list,
            report_date,
            report_doctor,
            check_doctor
        )
        self.setStyleSheet("background-color: white;")

    def init_UI(self,
                patient_ID,
                admission,
                examination,
                name,
                gender,
                age,
                check_date,
                department,
                bed,
                diagnose_result,
                doctor,
                material,
                visual,
                microscopic,
                path_diagnose,
                img_list,
                report_date,
                report_doctor,
                check_doctor):
        self.setWindowTitle("诊断报告")
        main_layout = QVBoxLayout(self)

        hostipal_label = QLabel("南方医科大学珠江医院")
        hostipal_label.setStyleSheet("font: bold 22px;")
        hostipal_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(hostipal_label)

        title_label = QLabel("病理检查报告单")
        title_label.setStyleSheet("font: bold 18px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        h_layout1 = QHBoxLayout()
        patient_ID_label = QLabel("病人ID：")
        self.patient_ID_text = QLabel(patient_ID)
        h_layout1.addWidget(patient_ID_label)
        h_layout1.addWidget(self.patient_ID_text)
        spacer0 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout1.addItem(spacer0)

        admission_label = QLabel("住院号")
        self.admission_text = QLabel(admission)
        h_layout1.addWidget(admission_label)
        h_layout1.addWidget(self.admission_text)
        spacer1 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout1.addItem(spacer1)

        examination_label = QLabel("病检号：")
        self.examination_text = QLabel(examination)
        h_layout1.addWidget(examination_label)
        h_layout1.addWidget(self.examination_text)

        main_layout.addLayout(h_layout1)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        h_layout2 = QHBoxLayout()
        name_label = QLabel("姓名：")
        self.name_text = QLabel(name)
        h_layout2.addWidget(name_label)
        h_layout2.addWidget(self.name_text)
        spacer2 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout2.addItem(spacer2)

        gender_label = QLabel("性别：")
        self.gender_text = QLabel(gender)
        h_layout2.addWidget(gender_label)
        h_layout2.addWidget(self.gender_text)
        spacer3 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout2.addItem(spacer3)

        age_label = QLabel("年龄：")
        self.age_text = QLabel(age)
        h_layout2.addWidget(age_label)
        h_layout2.addWidget(self.age_text)
        spacer4 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout2.addItem(spacer4)

        check_date_label = QLabel("检查日期：")
        self.check_date_text = QLabel(check_date)
        h_layout2.addWidget(check_date_label)
        h_layout2.addWidget(self.check_date_text)

        h_layout3 = QHBoxLayout()
        department_label = QLabel("申请科室：")
        self.department_text = QLabel(department)
        h_layout3.addWidget(department_label)
        h_layout3.addWidget(self.department_text)
        spacer5 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout3.addItem(spacer5)

        bed_label = QLabel("床号：")
        self.bed_text = QLabel(bed)
        h_layout3.addWidget(bed_label)
        h_layout3.addWidget(self.bed_text)
        spacer6 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout3.addItem(spacer6)

        diagnose_label = QLabel(f"临床诊断：")
        self.diagnose_text = QLabel(diagnose_result)
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
        self.doctor_text = QLabel(doctor)
        h_layout4.addWidget(doctor_label)
        h_layout4.addWidget(self.doctor_text)
        spacer8 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout4.addItem(spacer8)

        material_label = QLabel("送检材料：")
        self.material_text = QLabel(material)
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
        self.visual_text = QLabel(visual)
        self.visual_text.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.visual_text.setWordWrap(True)
        main_layout.addWidget(visual_label)
        main_layout.addWidget(self.visual_text)

        microscopic_label = QLabel("镜下检查：")
        self.microscopic_text = QLabel(microscopic)
        self.microscopic_text.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.microscopic_text.setWordWrap(True)
        main_layout.addWidget(microscopic_label)
        main_layout.addWidget(self.microscopic_text)

        path_diagnose_label = QLabel("病理诊断：")
        self.path_diagnose_text = QLabel(path_diagnose)
        self.path_diagnose_text.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.path_diagnose_text.setWordWrap(True)
        main_layout.addWidget(path_diagnose_label)
        main_layout.addWidget(self.path_diagnose_text)

        grid_layout = QGridLayout()
        cols = 2
        for idx, img_path in enumerate(img_list):
            h = int(idx / cols)
            w = idx % cols
            label = QLabel()
            pixmap = QPixmap(img_path)
            label.setPixmap(pixmap)
            grid_layout.addWidget(label, h, w, 1, 1)
        main_layout.addLayout(grid_layout)

        h_layout5 = QHBoxLayout()
        report_date_label = QLabel("报告日期：")
        report_date_text = QLabel(report_date)
        h_layout5.addWidget(report_date_label)
        h_layout5.addWidget(report_date_text)
        spacer10 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout5.addItem(spacer10)

        report_doctor_label = QLabel("报告医师：")
        report_doctor_text = QLabel(report_doctor)
        h_layout5.addWidget(report_doctor_label)
        h_layout5.addWidget(report_doctor_text)
        spacer11 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout5.addItem(spacer11)

        check_doctor_label = QLabel("审核医师：")
        check_doctor_text = QLabel(check_doctor)
        h_layout5.addWidget(check_doctor_label)
        h_layout5.addWidget(check_doctor_text)
        main_layout.addLayout(h_layout5)

        line3 = QFrame()
        line3.setFrameShape(QFrame.HLine)
        line3.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line3)

        warning_label1 = QLabel("温馨提示：本报告签字有效，如有疑问请及时余病理诊断医师联系，电话：020-63783360")
        warning_label2 = QLabel("        检查结果是依据送检标本的病理改变综合分析而定，有可能不包含全部病变，请注意结合临床。")
        main_layout.addWidget(warning_label1)
        main_layout.addWidget(warning_label2)

        spacer12 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        main_layout.addItem(spacer12)

