import json
import os
import sys

import time
import openslide
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import pyqtSignal, Qt, QTimer

from Inference.batch_process import BatchProcessThread
from function.utils import setFileWatcherDir, is_file_copy_finished

class MyLineEdit(QLineEdit):
    ClickSignal = pyqtSignal(bool)
    def __init__(self, name):
        super().__init__()
        self.emit_flag = False
        self.setText(name)
        self.setReadOnly(True)
        self.setAlignment(Qt.AlignHCenter)

    def mouseDoubleClickEvent(self, event):
        if self.emit_flag:
            self.ClickSignal.emit(True)

class FileWatcher(QWidget):
    openslideSignal = pyqtSignal(str, str)
    closeSignal = pyqtSignal(bool)
    def __init__(self, file_path):
        super(FileWatcher, self).__init__()
        self.path = file_path
        self.files = []
        self.whole_slide_formats = [
                                    "svs",
                                    "vms",
                                    "vmu",
                                    "ndpi",
                                    "scn",
                                    "mrx",
                                    "tiff",
                                    "svslide",
                                    "tif",
                                    "bif",
                                    "mrxs",
                                    "bif",
                                    "dmetrix",
                                    "qptiff"]
        if os.path.exists('cache/batch_process.json'):
            with open('cache/batch_process.json', 'r') as f:
                self.processed_list = json.load(f)
                f.close()
        else:
            self.processed_list = []


        self.init_UI()
        self.init_timer()
        # 初始化
        self.set_path(setFileWatcherDir())

    def init_UI(self):
        self.setWindowTitle("文件监控目录")
        icon = QIcon()
        icon.addPixmap(QPixmap('logo/logo.ico'))
        self.setWindowIcon(icon)
        self.table_widget = QTableWidget()
        self.table_widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table_widget.setColumnCount(6)
        self.table_widget.setHorizontalHeaderItem(0, QTableWidgetItem('文件名'))
        self.table_widget.setHorizontalHeaderItem(1, QTableWidgetItem('大小'))
        self.table_widget.setHorizontalHeaderItem(2, QTableWidgetItem('类型'))
        self.table_widget.setHorizontalHeaderItem(3, QTableWidgetItem('修改时间'))
        self.table_widget.setHorizontalHeaderItem(4, QTableWidgetItem('传输状态'))
        self.table_widget.setHorizontalHeaderItem(5, QTableWidgetItem("分析状态"))
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.cellClicked.connect(self.set_open)
        self.main_layout = QHBoxLayout(self)
        self.main_layout.addWidget(self.table_widget)
        self.set_style()

    # 初始化，增加path和检查slide能够打开的定时器
    def init_timer(self):
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_table)
        self.check_timer = QTimer(self)
        self.update_timer.timeout.connect(self.check_table)

    def getfileindir(self, root, file_name):
        file_path = os.path.join(root, file_name)
        # 如果是一个文件夹，则查看文件夹内的文件是否有病理图像文件
        if os.path.isdir(file_path):
            sub_files = os.listdir(file_path)
            for sub_file in sub_files:
                # 判断文件后缀是否为病理图像
                _, extension = os.path.splitext(sub_file)
                extension = extension.replace('.', '')
                if extension in self.whole_slide_formats:
                    file_path = os.path.join(file_path, sub_file)
                    return file_path, extension
        # 如果是一个文件，则判断是否为病理图像文件
        else:
            _, extension = os.path.splitext(file_path)
            extension = extension.replace('.', '')
            if extension in self.whole_slide_formats:
                return file_path, extension
        return None, None

    # 每次更改文件夹就会执行，初始化整个表单
    def init_table(self):
        self.files= []
        self.table_widget.clearContents()
        self.table_widget.setRowCount(0)
        file_names = sorted(os.listdir(self.path))
        row = 0
        for file_name in file_names:
            file_path, extension = self.getfileindir(self.path, file_name)
            if file_path is not None:
                self.add_table_item(os.path.basename(file_path), file_path, extension, row)
                self.files.append(file_path)
                row += 1
        self.update_timer.start(3000)
        self.check_timer.start(10000)

    # 查看当前的目录是否比之前的多，如果是，则添加到表单中
    def update_table(self):
        # 获取当前文件夹下左右的病理图像地址
        new_files = set([])
        file_names = sorted(os.listdir(self.path))
        for file_name in file_names:
            file_path, extension = self.getfileindir(self.path, file_name)
            if file_path is not None:
                new_files.add(file_path)
        # 将新的路径添加到表格中
        new_files = new_files - set(self.files.copy())
        for file_path in new_files:
            row = self.table_widget.rowCount()
            _, extension = os.path.splitext(file_path)
            extension = extension.replace('.', '')
            self.add_table_item(os.path.basename(file_path), file_path, extension, row)
            self.files.append(file_path)

    # 将item信息显示
    def add_table_item(self, file_name, file_path, extension, row):
        print(file_path)
        file_size = os.path.getsize(file_path)
        file_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(file_path)))
        self.table_widget.insertRow(row)
        self.table_widget.setItem(row, 0, QTableWidgetItem(file_name))
        self.table_widget.setItem(row, 1, QTableWidgetItem("{:.2f}MB".format(float(file_size/(1024*1024)))))
        self.table_widget.setItem(row, 2, QTableWidgetItem(extension))
        self.table_widget.setItem(row, 3, QTableWidgetItem(file_time))
        # 设置传输状态和分析状态
        self.table_widget.setItem(row, 4, QTableWidgetItem('正在传输'))

        if file_name in self.processed_list:
            self.table_widget.setItem(row, 5, QTableWidgetItem('诊断完成'))
        else:
            self.table_widget.setItem(row, 5, QTableWidgetItem('等待分析'))

    # 检查文件是否传输完成
    def check_table(self):
        row_count = self.table_widget.rowCount()
        file_list = self.files
        if len(file_list) != row_count:
            return
        for row in range(row_count):
            file_path = file_list[row]
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                self.table_widget.setItem(row, 1, QTableWidgetItem("{:.2f}MB".format(float(file_size / (1024 * 1024)))))
            else:
                self.table_widget.setItem(row, 1, QTableWidgetItem("{:.2f}MB".format(float(0))))
                self.table_widget.setItem(row, 4, QTableWidgetItem('文件丢失'))
                continue
            if self.table_widget.item(row, 4).text() == "传输完成":
                if not os.path.exists(file_path):
                    self.table_widget.setItem(row, 1, QTableWidgetItem("{:.2f}MB".format(float(0))))
                    self.table_widget.setItem(row, 4, QTableWidgetItem('文件丢失'))
                elif is_file_copy_finished(file_path) is False:
                    self.table_widget.setItem(row, 4, QTableWidgetItem('正在传输'))
                continue
            try:
                if is_file_copy_finished(file_path):
                    self.table_widget.setItem(row, 4, QTableWidgetItem('传输完成'))
                else:
                    self.table_widget.setItem(row, 4, QTableWidgetItem('正在传输'))
            except:
                self.table_widget.setItem(row, 4, QTableWidgetItem('正在传输'))

    def set_style(self):
        self.setStyleSheet("QHeaderView::section{font-family:微软雅黑; font: bold 15px;font-weight:400}"
                           "QLineEdit{font-family:微软雅黑;font: bold 14px;font-weight:100}")

    # 重新设置文件监控的目录
    def set_path(self, path):
        if path is not None:
            try:
                self.update_timer.stop()
                self.check_timer.stop()
            except:
                pass
            self.path = path
            self.init_table()

    def closeEvent(self, event):
        super().closeEvent(event)
        self.closeSignal.emit(True)

    # 点击打开文件窗口,如果批处理完成，则直接打开处理后的结果
    def set_open(self, row, col):
        if col == 0:
            file_list = self.files
            if len(file_list) != self.table_widget.rowCount():
                return
            if self.table_widget.item(row, 4).text() == '传输完成':
                file_path = file_list[row]
                if is_file_copy_finished(file_path) is False:
                    return
                try:
                    slide = openslide.open_slide(file_path)
                    if self.table_widget.item(row, 5).text() == '诊断完成':
                        self.openslideSignal.emit(file_path, '诊断')
                    elif self.table_widget.item(row, 5).text() == '微环境分析完成':
                        self.openslideSignal.emit(file_path, '微环境分析')
                    elif self.table_widget.item(row, 5).text() == 'PD-L1测量完成':
                        self.openslideSignal.emit(file_path, 'PD-L1测量')
                    else:
                        self.openslideSignal.emit(file_path, '')
                except:
                    QMessageBox.warning(self, '警告', f'该文件无法打开')
            else:
                QMessageBox.warning(self, '警告', f'该文件{self.table_widget.item(row, 4).text()}')
                return

    def batch_process(self):
        if hasattr(self, 't'):
            if self.t.isRunning():
                QMessageBox.warning(self, '警告', '正在执行批处理')
                return

        # 创建对话框对象
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("选择处理模式")
        # 添加自定义按钮
        custom_btn1 = msg_box.addButton('诊断', QMessageBox.YesRole)
        custom_btn2 = msg_box.addButton('微环境分析', QMessageBox.YesRole)
        custom_btn3 = msg_box.addButton('PD-L1测量', QMessageBox.YesRole)
        custom_btn4 = msg_box.addButton('取消', QMessageBox.RejectRole)
        custom_btn2.setEnabled(False)
        custom_btn3.setEnabled(False)
        # 弹出对话框并等待用户响应
        result = msg_box.exec_()
        # 根据用户的选择来进行处理
        if msg_box.clickedButton() == custom_btn1:
            mode = '诊断'
        elif msg_box.clickedButton() == custom_btn2:
            mode = '微环境分析'
            return
        elif msg_box.clickedButton() == custom_btn3:
            mode = 'PD-L1测量'
            return
        else:
            return
        self.t = BatchProcessThread(self, mode, self.path)
        self.t.batch_flag = True
        self.t.start()

    def stop_batch_process(self):
        if hasattr(self, 't'):
            self.t.batch_flag = False

    def set_style(self):
        self.setStyleSheet("QLabel{font-family:微软雅黑; font: bold 16px;}")

    def __del__(self):
        if hasattr(self, 't'):
            if self.t.isRunning():
                return