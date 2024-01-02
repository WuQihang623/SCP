import json
import os

import time
import constants
import openslide
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import pyqtSignal, Qt, QTimer, QThread

# from Inference.batch_process import BatchProcessThread
from function.utils import setFileWatcherDir, is_file_copy_finished

# 获取再文件夹中的病理图像文件
def getfileindir(root, file_name):
    whole_slide_formats = [
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
    file_path = os.path.join(root, file_name)
    # 如果是一个文件夹，则查看文件夹内的文件是否有病理图像文件
    if os.path.isdir(file_path):
        sub_files = os.listdir(file_path)
        for sub_file in sub_files:
            # 判断文件后缀是否为病理图像
            _, extension = os.path.splitext(sub_file)
            extension = extension.replace('.', '')
            if extension in whole_slide_formats:
                file_path = os.path.join(file_path, sub_file)
                return file_path, extension
    # 如果是一个文件，则判断是否为病理图像文件
    else:
        _, extension = os.path.splitext(file_path)
        extension = extension.replace('.', '')
        if extension in whole_slide_formats:
            return file_path, extension
    return None, None

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

class UpdateTableThread(QThread):
    add_table_signal = pyqtSignal(int, str)
    check_table_signal = pyqtSignal(int, str, int, str)
    timer_sinal = pyqtSignal()

    def __init__(self, dir_path):
        super(UpdateTableThread, self).__init__()
        self.dir_path = dir_path
        self.file_info = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(10000)
        self.start(QThread.LowestPriority)

    def update(self):
        if self.isRunning():
            self.wait()
        self.start(QThread.LowestPriority)

    def run(self):
        """检查文件夹中是否有新的文件进来"""
        new_files = set([])
        # 如果该路径不存在，则退出线程
        if not os.path.exists(self.dir_path):
            return
        file_names = sorted(os.listdir(self.dir_path))
        for file_name in file_names:
            file_path, extension = getfileindir(self.dir_path, file_name)
            if file_path is not None:
                new_files.add(file_path)

        # 将新的文件发送给filewatcher
        new_files = new_files - set(self.file_info.copy())
        new_files = sorted(new_files)
        for file_path in new_files:
            self.add_table_signal.emit(len(self.file_info), file_path)
            self.file_info.append(file_path)

        """检查文件传输状态"""
        for row, file_path in enumerate(self.file_info):
            # 如果该路劲存在，则计算文件的大小
            # 如果文件不存在，则将文件状态设置为文件丢失
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                try:
                    if is_file_copy_finished(file_path):
                        file_status = "传输完成"
                    else:
                        file_status = "正在传输"
                except:
                    file_status = "正在传输"
                self.check_table_signal.emit(row, file_path, file_size, file_status)
            else:
                file_size = 0
                file_status = "文件丢失"
                self.check_table_signal.emit(row, file_path, file_size, file_status)

    def restart(self, dir_path):
        self.dir_path = dir_path
        self.file_info = []
        self.start(QThread.LowestPriority)

class FileWatcher(QWidget):
    openslideSignal = pyqtSignal(str, str)
    closeSignal = pyqtSignal(bool)
    BatchProcessPath = os.path.join(constants.cache_path, "batch_process.json")
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

        # 批处理状态
        if os.path.exists(self.BatchProcessPath):
            with open(self.BatchProcessPath, 'r') as f:
                self.processed_list = json.load(f)
                f.close()
        else:
            self.processed_list = []

        self.init_UI()

        self.update_table = UpdateTableThread(self.path)
        self.update_table.add_table_signal.connect(self.add_table_item)
        self.update_table.check_table_signal.connect(self.modify_tabel_item)

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

    def add_table_item(self, row, file_path):
        self.files.append(file_path)
        _, extension = os.path.splitext(file_path)
        extension = extension.replace('.', '')
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        file_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(file_path)))
        self.table_widget.insertRow(row)
        self.table_widget.setItem(row, 0, QTableWidgetItem(file_name))
        self.table_widget.setItem(row, 1, QTableWidgetItem("{:.2f}MB".format(float(file_size / (1024 * 1024))).replace('-', '')))
        self.table_widget.setItem(row, 2, QTableWidgetItem(extension))
        self.table_widget.setItem(row, 3, QTableWidgetItem(file_time))
        # 设置传输状态和分析状态
        self.table_widget.setItem(row, 4, QTableWidgetItem('正在传输'))

        if file_name in self.processed_list:
            self.table_widget.setItem(row, 5, QTableWidgetItem('诊断完成'))
        else:
            self.table_widget.setItem(row, 5, QTableWidgetItem('等待分析'))

    def modify_tabel_item(self, row, file_path, file_size, file_status):
        item = self.table_widget.item(row, 0)
        if item is not None:
            file_name = item.text()
            # 确认该行的文件是传输过来的那个
            if file_name == os.path.basename(file_path):
                self.table_widget.setItem(row, 1, QTableWidgetItem("{:.2f}MB".format(float(file_size / (1024 * 1024))).replace('-', '')))
                self.table_widget.setItem(row, 4, QTableWidgetItem(file_status))
                self.table_widget.update()


    # 重置tablewidget
    def reset(self):
        self.table_widget.clearContents()
        self.table_widget.setRowCount(0)
        self.files = []

    # 重新设置文件监控的目录
    def set_path(self, path):
        if path is not None:
            try:
                if self.update_table.isRunning():
                    self.update_table.wait()
            except:
                pass
            self.path = path
            self.reset()
            self.update_table.restart(path)

    def start_timer(self):
        try:
            self.update_table.timer.start()
            print("start file watch")
        except:
            return

    def stop_timer(self):
        try:
            self.update_table.timer.stop()
            print("stop file watch")
        except:
            return


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

    # def batch_process(self):
    #     if hasattr(self, 't'):
    #         if self.t.isRunning():
    #             QMessageBox.warning(self, '警告', '正在执行批处理')
    #             return
    #
    #     # 创建对话框对象
    #     msg_box = QMessageBox(self)
    #     msg_box.setWindowTitle("选择处理模式")
    #     # 添加自定义按钮
    #     custom_btn1 = msg_box.addButton('诊断', QMessageBox.YesRole)
    #     custom_btn2 = msg_box.addButton('微环境分析', QMessageBox.YesRole)
    #     custom_btn3 = msg_box.addButton('PD-L1测量', QMessageBox.YesRole)
    #     custom_btn4 = msg_box.addButton('取消', QMessageBox.RejectRole)
    #     custom_btn2.setEnabled(False)
    #     custom_btn3.setEnabled(False)
    #     # 弹出对话框并等待用户响应
    #     result = msg_box.exec_()
    #     # 根据用户的选择来进行处理
    #     if msg_box.clickedButton() == custom_btn1:
    #         mode = '诊断'
    #     elif msg_box.clickedButton() == custom_btn2:
    #         mode = '微环境分析'
    #         return
    #     elif msg_box.clickedButton() == custom_btn3:
    #         mode = 'PD-L1测量'
    #         return
    #     else:
    #         return
    #     self.t = BatchProcessThread(self, mode, self.path)
    #     self.t.batch_flag = True
    #     self.t.start()
    #
    # def stop_batch_process(self):
    #     if hasattr(self, 't'):
    #         self.t.batch_flag = False

    def set_style(self):
        self.setStyleSheet("QLabel{font-family:宋体; font: bold 14px;}")

    def closeEvent(self, event):
        if hasattr(self, 't'):
            if self.t.isRunning():
                QMessageBox.warning(self, '提示', '批处理未停止，请先等待批处理结束')
                event.ignore()
                return
        self.closeSignal.emit(True)
        print("关闭文件监控")
        return super(FileWatcher, self).closeEvent(event)