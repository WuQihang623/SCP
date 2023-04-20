import json
import os
import sys

import cv2
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal, QEvent
from window.UI.UI_diagnose import UI_Diagnose
from PIL.ImageQt import ImageQt
from PyQt5.QtGui import QPixmap
from window.slide_window.utils.SlideHelper import SlideHelper
from window.slide_window.utils.MyGraphicsPixmapItem import MyGraphicsPixmapItem
from Inference.diagnose.diagnose import Thread_Diagnose
from Inference.progress_bar import progress_dialog


class DiagnoseWidget(UI_Diagnose):
    loadDiagnoseSignal = pyqtSignal(str)
    # 发送诊断框
    sendDiagnoseRectSignal = pyqtSignal(list)
    # 发送诊断框索引
    sendDiagnoseRectIdxSignal = pyqtSignal(int)
    # 诊断进度条
    bar_signal_diagnose = pyqtSignal(int, int, str)
    def __init__(self):
        super(DiagnoseWidget, self).__init__()
        self.file_dir = './'

        self.btn_connect()

    def btn_connect(self):
        self.loadDiagnoseResults_btn.clicked.connect(self.load_result)
        self.diagnose_btn.clicked.connect(self.diagnose)

    # 加载诊断结论
    def setText(self, preds):
        if preds is not None:
            if preds > 0.5:
                self.diagnoseConclusion_label.setText("诊断结果：阳性")
                self.diagnoseProb_label.setText("置信度：{}%".format(int(preds * 100)))
            else:
                self.diagnoseConclusion_label.setText("诊断结果：阴性")
                self.diagnoseConclusion_label.setText("置信度：{}%".format(int(100 - preds * 100)))
        else:
            self.diagnoseConclusion_label.setText("诊断结果:")
            self.diagnoseProb_label.setText("置信度:")

    # 离线载入淋巴结转移结果
    def load_result(self, path):
        slide_name, _ = os.path.splitext(os.path.basename(self.slide_path))
        # 如果不存在，就根据当前文本框的路径加上文件名设置默认的载入路径
        if not os.path.exists(path) or not isinstance(path, str):
            # options = QFileDialog.Options()
            # path, _ = QFileDialog.getOpenFileName(self, "选择诊断结果存放的路径", self.file_dir,
            #                                       "热图(*.jpg)", options=options)
            path = os.path.join(self.folderselector.FileDir(), 'Diagnose', slide_name, f"{slide_name}_result.jpg")
        if not os.path.exists(path):
            QMessageBox.warning(self, '警告', '路径不存在！')
            return
        if slide_name not in path:
            QMessageBox.warning(self, '警告', '结果文件与图片不匹配！')
            return
        self.file_dir = os.path.dirname(path)
        self.loadDiagnoseSignal.emit(path)
        self.showHeatmap_btn.setChecked(True)

        # 加载预测结果
        preds_path = path.replace('result.jpg', 'preds_down.json')
        with open(preds_path, 'r') as f:
            self.preds = json.load(f)
            f.close()
        self.setText(self.preds['preds'])

        # 加载预测mask
        size = 256
        probs_path = path.replace('result.jpg', 'probs.npy')
        self.probs = np.load(probs_path)
        probs_shape = (int(self.slide_helper.get_level_dimension(0)[0] / size),
                       int(self.slide_helper.get_level_dimension(0)[1] / size))
        self.probs = cv2.resize(self.probs, probs_shape, cv2.INTER_LINEAR)
        self.scene.setSceneRect(0, 0, 256, (256 + 10) * 50)
        probs_1d = self.probs.flatten()
        idx_1d = probs_1d.argsort()[-50:]
        y_idx, x_idx = np.unravel_index(idx_1d, self.probs.shape)
        downsample = self.slide_helper.get_level_dimension(0)[0] / self.probs.shape[1]
        num = 0
        self.rect_list = []
        for x, y in zip(x_idx, y_idx):
            if self.probs[y][x] > 0.5:
                original_x = int(x * downsample)
                original_y = int(y * downsample)
                level = 0
                if level > self.slide_helper.get_max_level():
                    level = self.slide_helper.get_max_level()
                pil_image = self.slide_helper.read_region((original_x, original_y), level, (size, size))
                pixmap = self.pilimage_to_pixmap(pil_image)
                item = MyGraphicsPixmapItem(pixmap, num)
                item.setScale(256 / size)
                item.setPos(0, num * (256 + 10))
                self.scene.addItem(item)
                self.rect_list.append([original_x, original_y, size, size])
                num += 1
        self.sendDiagnoseRectSignal.emit(self.rect_list)

    def pilimage_to_pixmap(self, pilimage):
        qim = ImageQt(pilimage)
        pix = QPixmap.fromImage(qim)
        return pix

    def set_slide_path(self, slide_path):
        self.slide_path = slide_path
        self.slide_helper = SlideHelper(slide_path)

    # 点击某个矩形，则将画面跳转到那个视图下
    def mousePressEvent(self, event):
        if event.type() == QEvent.MouseButtonPress:
            item = self.view.itemAt(event.pos())
            if hasattr(item, 'key'):
                self.sendDiagnoseRectIdxSignal.emit(item.key - 1)

    def diagnose(self):
        kwargs = {"slidepath": self.slide_helper.slide_path,
                  'signal': self.bar_signal_diagnose}
        self.diagnose_thread = Thread_Diagnose(kwargs, self.slide_helper.get_level_dimension(-1))
        self.diagnose_dialog = progress_dialog("乳腺癌淋巴结转移诊断", '正在进行诊断……')
        self.bar_signal_diagnose.connect(self.diagnose_dialog.call_back)
        self.diagnose_thread.complete_signal.connect(self.load_result)
        self.diagnose_thread.start()
        self.diagnose_dialog.start()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # app.setStyleSheet(qdarkstyle.load_stylesheet())
    window = DiagnoseWidget()
    window.show()
    sys.exit(app.exec_())
