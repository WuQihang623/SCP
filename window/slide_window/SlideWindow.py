import os
import numpy as np
import constants
from skimage.transform import estimate_transform
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QKeySequence, QCursor
from window.slide_window import *
from PyQt5.QtCore import Qt, pyqtSignal
from window.Controller_Widget import Controller
from window.slide_window.utils.AffirmDialog import CloseDialog
from window.dialog.RegionstrationDialog import RegistrationTipDialog, RegistrationDialog

class SlideWindow(QFrame):
    lockMoveModeSignal = pyqtSignal(bool)
    def __init__(self, file_path):
        super(SlideWindow, self).__init__()
        self.init_UI()
        self.mainViewerLoadSlide(file_path)

    def init_UI(self):
        main_layout = QVBoxLayout(self)
        self.mainViewer = SlideViewer()
        self.sideViewer = SlideViewer(mainViewerFlag=False)
        self.controller = Controller()
        self.splitter_viewer = QSplitter(Qt.Horizontal)
        self.splitter_viewer.addWidget(self.mainViewer)
        self.splitter_viewer.addWidget(self.sideViewer)
        self.splitter_viewer.setHandleWidth(0)
        handle = self.splitter_viewer.handle(1)
        handle.setEnabled(False)
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.controller)
        self.splitter.addWidget(self.splitter_viewer)
        self.splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.splitter.setSizes([300, 1000])
        self.splitter_viewer.setSizes([1, 1])
        self.splitter_viewer.widget(1).hide()
        main_layout.addWidget(self.splitter)

    def mainViewerInitSignalSlotConnections(self):
        """
            初始化mainViewer的信号与槽
        """
        # 标注
        # 导入标注时，设置choosed_idx
        self.controller.syncAnnotationSignal.connect(self.mainViewer.ToolManager.syncAnnotation)
        # 导入标注后，绘制所有的标注
        self.controller.showAnnotationSignal.connect(self.mainViewer.show_annotation_slot)
        # 改变标注的颜色或者类型
        self.controller.changeAnnotationItemSignal.connect(self.mainViewer.ToolManager.changeAnnotation)
        # 点击标注时，跳转到该标注视图位置
        self.controller.updateChoosedAnnotationSignal.connect(self.mainViewer.ToolManager.switch2choosedItem)
        # 将修改的标注坐标信息转递给Controller
        self.mainViewer.ToolManager.sendModifiedAnnotationSignal.connect(self.controller.modify_annotation_slot)
        # 切换标注工具
        self.controller.toolChangeSignal.connect(self.mainViewer.ToolManager.set_annotation_mode)
        # 切换标注类型
        self.controller.annotationTypeChooseSignal.connect(self.mainViewer.ToolManager.set_annotationColor)
        # 绘制完标注后添加
        self.mainViewer.ToolManager.sendAnnotationSignal.connect(self.controller.addAnnotaton)
        self.controller.deleteAnnotationSignal.connect(self.mainViewer.ToolManager.deleteAnnotation)
        self.controller.changeAnnotaionSignal.connect(self.mainViewer.ToolManager.changeAnnotation)

        self.mainViewer.ToolManager.switch2choosedItemSignal.connect(self.mainViewer.switch2annotation)
        self.mainViewer.reactivateItemSignal.connect(self.mainViewer.ToolManager.reactivateItem)

        self.mainViewer.load_nucleus_action.triggered.connect(lambda : self.controller.load_nucleus_signal_fn(True))
        self.mainViewer.load_heatmap_action.triggered.connect(lambda : self.controller.load_heatmap_signal_fn(True))
        self.mainViewer.load_contour_action.triggered.connect(lambda : self.controller.load_contour_signal_fn(True))
        self.mainViewer.load_nucleus_diff_action.triggered.connect(lambda : self.controller.load_nucleus_diff_signal_fn(True))

        self.controller.mainViewerloadNucleusSignal.connect(self.mainViewer.load_nucleus_slot)
        self.controller.mainViewerloadheatmapSignal.connect(self.mainViewer.load_heatmap_slot)
        self.controller.mainViewerloadContourSignal.connect(self.mainViewer.load_contour_slot)
        self.controller.mainViewerloadNucleusDiffSignal.connect(self.mainViewer.load_nucleus_diff_slot)

        self.controller.viewerShowNucleusSignal.connect(self.mainViewer.show_nucleus_slot)
        self.controller.viewerShowHeatmapSignal.connect(self.mainViewer.show_heatmap_slot)
        self.controller.viewerShowContourSignal.connect(self.mainViewer.show_contour_slot)
        self.controller.viewerShowNucleusDiffSignal.connect(self.mainViewer.show_nucleus_diff_slot)

        """快捷键"""
        # self.saveAnnShortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        # self.stopDrawShortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        # self.deleteAnnShortcut = QShortcut(QKeySequence(Qt.Key_Delete), self)
        # self.full_screenShortcut = QShortcut(QKeySequence(Qt.Key_Q), self)
        # self.saveAnnShortcut.activated.connect(self.saveAnnotations)
        # self.stopDrawShortcut.activated.connect(self.stopDraw)
        # self.deleteAnnShortcut.activated.connect(self.deleteAnnotation)
        # self.full_screenShortcut.activated.connect(self.full_screen)

    def sideViewerInitSignalSlotConnections(self):
        """
            初始化sideViewer的信号与槽
        """
        self.sideViewer.load_nucleus_action.triggered.connect(lambda: self.controller.load_nucleus_signal_fn(False))
        self.sideViewer.load_heatmap_action.triggered.connect(lambda: self.controller.load_heatmap_signal_fn(False))
        self.sideViewer.load_contour_action.triggered.connect(lambda: self.controller.load_contour_signal_fn(False))
        self.sideViewer.load_nucleus_diff_action.triggered.connect(lambda: self.controller.load_nucleus_diff_signal_fn(False))

        self.controller.sideViewerloadNucleusSignal.connect(self.sideViewer.load_nucleus_slot)
        self.controller.sideViewerloadheatmapSignal.connect(self.sideViewer.load_heatmap_slot)
        self.controller.sideViewerloadContourSignal.connect(self.sideViewer.load_contour_slot)
        self.controller.sideViewerloadNucleusDiffSignal.connect(self.sideViewer.load_nucleus_diff_slot)

        self.controller.viewerShowNucleusSignal.connect(self.sideViewer.show_nucleus_slot)
        self.controller.viewerShowHeatmapSignal.connect(self.sideViewer.show_heatmap_slot)
        self.controller.viewerShowContourSignal.connect(self.sideViewer.show_contour_slot)
        self.controller.viewerShowNucleusDiffSignal.connect(self.sideViewer.show_nucleus_diff_slot)

    def mainViewerLoadSlide(self, slide_path, zoom_step=1.15):
        """
            将WSI加载到mainViewer中
        """
        self.mainViewer.loadSlide(slide_path=slide_path, zoom_step=zoom_step)
        self.controller.setMainViewerName(slide_path=slide_path)
        self.mainViewerInitSignalSlotConnections()

    def sideViewerLoadSlide(self, slide_path, zoom_step=1.15):
        """
            将WSI加载到sideViewer中
        """
        self.sideViewer.loadSlide(slide_path=slide_path, zoom_step=zoom_step)
        self.controller.setSideViewerName(slide_path=slide_path)
        self.sideViewerInitSignalSlotConnections()
        self.sideViewer.addAction2Menu([])

        # 显示副窗口
        if not self.splitter_viewer.widget(1).isVisible():
            self.splitter_viewer.widget(1).show()

    def RegistrationSigalSlotConnections(self, transform_matrix):
        self.mainViewer.initRegistration(np.linalg.inv(transform_matrix), Registration=True)
        self.sideViewer.initRegistration(transform_matrix, Registration=True)

        self.mainViewer.moveTogetherSignal.connect(self.sideViewer.move_together)
        self.sideViewer.moveTogetherSignal.connect(self.mainViewer.move_together)

        self.mainViewer.scaleTogetherSignal.connect(self.sideViewer.scale_together)
        self.sideViewer.scaleTogetherSignal.connect(self.mainViewer.scale_together)

        self.sideViewer.receive_match(*self.mainViewer.send_match())

        self.mainViewer.pairMouseSignal.connect(self.sideViewer.draw_mouse)
        self.sideViewer.pairMouseSignal.connect(self.mainViewer.draw_mouse)

        self.mainViewer.clearMouseSignal.connect(self.sideViewer.remove_mouse)
        self.sideViewer.clearMouseSignal.connect(self.mainViewer.remove_mouse)

        info_dialog = QMessageBox()
        info_dialog.setWindowTitle("仿射变换矩阵")
        info_dialog.setText(f"图像配准成功\n仿射变换矩阵为:\n{np.linalg.inv(transform_matrix)}")
        info_dialog.exec_()

    def cancelRegistration(self):
        """
            取消配准
        """
        if hasattr(self.sideViewer, "TileLoader"):
            if self.mainViewer.Registration:
                self.mainViewer.initRegistration(None, Registration=False)
                self.sideViewer.initRegistration(None, Registration=False)

                self.mainViewer.moveTogetherSignal.disconnect(self.sideViewer.move_together)
                self.sideViewer.moveTogetherSignal.disconnect(self.mainViewer.move_together)

                self.mainViewer.scaleTogetherSignal.disconnect(self.sideViewer.scale_together)
                self.sideViewer.scaleTogetherSignal.disconnect(self.mainViewer.scale_together)

                self.mainViewer.pairMouseSignal.disconnect(self.sideViewer.draw_mouse)
                self.sideViewer.pairMouseSignal.disconnect(self.mainViewer.draw_mouse)

                self.mainViewer.clearMouseSignal.disconnect(self.sideViewer.remove_mouse)
                self.sideViewer.clearMouseSignal.disconnect(self.mainViewer.remove_mouse)
            else:
                QMessageBox.warning(self, "提示", "图像没有进行配准！")

    def hookSlideViewer(self):
        """
            手动选择点，用于将mainViewer和sideViewer配对上
        """
        # 如果没有载入对比结果则跳过
        if not hasattr(self.sideViewer, "TileLoader"):
            QMessageBox.warning(self, "警告", "没有载入副窗口！")
            return
        # 如果副窗口被隐藏，则打开
        if not self.splitter_viewer.widget(1).isVisible():
            self.splitter_viewer.widget(1).show()

        dialog = RegistrationDialog()
        if dialog.exec_() == QDialog.Accepted:
            # 如果之前已经配准过了，那么要取消掉重新配准
            if self.mainViewer.Registration:
                self.cancelRegistration()
            if dialog.get_mode() == "manual":
                """
                    手动选择n个点进行配准
                """
                # TODO: 设置为移动模式，不能进行标注，并且不能切换标注工具
                self.lockMoveModeSignal.emit(True)
                # 设置标志位，使得双击的时候可以选点
                self.mainViewer.ToolManager.set_registration_flag(True)
                self.sideViewer.ToolManager.set_registration_flag(True)

                transform_matrix = self.manualFindMatchPoint()

                # 设置slide_viewer关闭标点模式
                self.slide_viewer.ToolManager.set_registration_flag(False)
                self.slide_viewer_pair.ToolManager.set_registration_flag(False)

                self.lockMoveModeSignal.emit(False)
                if transform_matrix is None:
                    return

            elif dialog.get_mode() == "same":
                """
                    相同的WSI
                """
                transform_matrix = np.array([[1, 0, 0],
                                             [0, 1, 0],
                                             [0, 0, 1]])

            else:
                """
                    载入一个transform矩阵
                """
                options = QFileDialog.Options()
                path, _ = QFileDialog.getOpenFileName(self, "选择配准矩阵", f"{constants.cache_path}", "*(*.npy)",
                                                      options=options)
                if path == '' or not os.path.exists(path): return
                transform_matrix = np.load(path)
                transform_matrix = np.linalg.inv(transform_matrix)

            self.RegistrationSigalSlotConnections(transform_matrix)

            if dialog.get_mode() == "manual":
                slide_name = os.path.splitext(os.path.basename(self.mainViewer.slide_helper.slide_path))[0]
                np.save(f"{constants.cache_path}/{slide_name}.npy", np.linalg.inv(transform_matrix))

        else:
            return


    def manualFindMatchPoint(self):
        """
            手工获取匹配的点
        """
        while True:
            tip_dialog = RegistrationTipDialog()
            tip_dialog.setWindowFlag(Qt.WindowStaysOnTopHint, True)
            tip_dialog.show()
            reply = tip_dialog.exec_()
            if reply == QDialog.Accepted:
                points1 = self.mainViewer.ToolManager.draw_point.get_registration_points()
                points2 = self.sideViewer.ToolManager.draw_point.get_registration_points()
                if len(points1) < 4 or len(points2) < 4:
                    QMessageBox.warning(self, "警告", "要求至少在图中各选择4个点位！")
                elif len(points1) != len(points2):
                    if len(points1) < len(points2):
                        QMessageBox.warning(self, "警告", f"请在左边再选{len(points2) - len(points1)}个点")
                    else:
                        QMessageBox.warning(self, "警告", f"请在右边再选{len(points1) - len(points2)}个点")
                else:
                    # 计算仿射变换矩阵
                    points1 = np.array(points1)
                    points2 = np.array(points2)
                    transform_matrix = estimate_transform('affine', points2, points1)
                    print("transform matrix", transform_matrix)
                    return transform_matrix
            else:
                return None

    def saveAnnotations(self):
        """
            快捷键保存标注
        """
        # if hasattr(self, 'annotation'):
        #     # 如果当前激活的是标注模式
        #     if self.splitter.widget(0).isVisible():
        #         self.annotation.saveAnnotations()

    # 快捷键--停止当前标注
    def stopDrawAnnotation(self):
        """
            快捷键： 停止进行当前标注
        """
        # if hasattr(self, 'annotation'):
        #     # 如果时标注模式
        #     if self.splitter.widget(0).isVisible():
        #         self.mainViewer.ToolManager.cancel_drawing()

    def fullScreen(self):
        """
            切换到全屏模式
        """
        # if hasattr(self, "mainViewer") and self.isActiveWindow():
        #     if self.full_screen_flag:
        #         # 恢复正常屏幕
        #         self.setWindowFlags(Qt.SubWindow)
        #         self.showNormal()
        #         self.showMaximized()
        #         self.full_screen_flag = False
        #     else:
        #         # 全屏
        #         # # 获取鼠标的当前位置
        #         cursor = QCursor()
        #         cursor_pos = cursor.pos()
        #         # 获取包含鼠标位置的屏幕
        #         screen = QDesktopWidget().screenNumber(cursor_pos)
        #         screen_geometry = QDesktopWidget().screenGeometry(screen)
        #         # 将窗口设置为包含鼠标位置的屏幕的工作区域
        #         self.setGeometry(screen_geometry)
        #         self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        #         self.showFullScreen()
        #         self.full_screen_flag = True


    def deleteAnnotation(self):
        """
            快捷键--删除选中标注
        """
        # if hasattr(self, 'annotation'):
        #     # 如果时标注模式
        #     if self.splitter.widget(0).isVisible():
        #         self.annotation.deleteAnnotation()

    def closeEvent(self, event):
        """
            关闭窗口的时候保存标注
        """
        if hasattr(self, 'controller') is False:
            return

        if self.controller.annotation:
            text = os.path.basename(self.controller.mainViewer_name)
            dialog = CloseDialog(f"是否要保存{text}标注？")
            if dialog.exec_() == QDialog.Accepted:
                if dialog.text == '保存':
                    self.controller.save_annotation_slot()
                else:
                    event.accept()
            else:
                event.ignore()
                return

        self.mainViewer.closeEvent()
        self.sideViewer.closeEvent()
        self.controller.closeEvent(event)
        return


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = SlideWindow("E:/dataset/SYMH/HE/463042.qptiff")
    window.show()
    sys.exit(app.exec_())

