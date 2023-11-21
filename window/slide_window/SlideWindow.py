import os

import pickle
import numpy as np
import constants
from skimage.transform import estimate_transform
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QKeySequence, QCursor, QScreen
from window.slide_window import *
from PyQt5.QtCore import Qt, pyqtSignal
from window.slide_window.utils.AffirmDialog import CloseDialog
from window.slide_window.utils.RegistrationDialog import RegistrationDialog
from window.slide_window.utils.RegistrationTipDialog import RegistrationTipDialog

class SlideWindow(QFrame):
    lockModeSignal = pyqtSignal(bool)
    def __init__(self, file_path):
        super(SlideWindow, self).__init__()
        self.init_UI()
        self.load_slide(file_path)
        # 初始化快捷键
        self.init_shortcut()
        # 连接槽函数
        self.connectSignalSlot()
        # 设置初始化的颜色
        self.annotation.set_AnnotationColor(0)
        self.full_screen_flag = False

    def init_UI(self):
        main_layout = QVBoxLayout(self)
        self.slide_viewer = SlideViewer()
        self.slide_viewer_pair = SlideViewer(paired=True)
        self.annotation = AnnotationWidget()
        self.diagnose = DiagnoseWidget()
        self.microenv = MicroenvWidget()
        self.pdl1 = PDL1Widget()
        self.multimodal = MultimodalWidget()

        self.splitter_viewer = QSplitter(Qt.Horizontal)

        self.splitter_viewer.addWidget(self.slide_viewer)
        self.splitter_viewer.addWidget(self.slide_viewer_pair)
        self.splitter_viewer.setHandleWidth(0)
        handle = self.splitter_viewer.handle(1)
        handle.setEnabled(False)

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.annotation)
        self.splitter.addWidget(self.diagnose)
        self.splitter.addWidget(self.microenv)
        self.splitter.addWidget(self.pdl1)
        self.splitter.addWidget(self.multimodal)
        self.splitter.addWidget(self.splitter_viewer)
        self.splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.splitter.setSizes([300, 300, 300, 300, 300, 1000])
        self.splitter_viewer.setSizes([1, 1])
        for i in range(1, 5):
            self.splitter.widget(i).hide()
        self.splitter_viewer.widget(1).hide()

        main_layout.addWidget(self.splitter)

    # 初始化快捷键
    def init_shortcut(self):
        self.saveAnnShortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.stopDrawShortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.deleteAnnShortcut = QShortcut(QKeySequence(Qt.Key_Delete), self)
        self.full_screenShortcut = QShortcut(QKeySequence(Qt.Key_Q), self)

    # 连接信号与槽
    def connectSignalSlot(self):
        """标注模式的信号"""
        # 切换模式时，将ToolManager中的标志位切换了，实现工具的切换
        self.annotation.toolChangeSignal.connect(self.slide_viewer.ToolManager.set_annotation_mode)
        # 切换颜色，将ToolManager中的颜色与类型切换了
        self.annotation.annotationTypeChooseSignal.connect(self.slide_viewer.ToolManager.set_annotationColor)
        # 绘制完成标注后，将标注的内容添加到annotaionTree中
        self.slide_viewer.ToolManager.sendAnnotationSignal.connect(self.annotation.addAnnotation)
        # 点击标注栏中的item，获取该标注在视图中的位置
        self.annotation.updateChoosedItemSignal.connect(self.slide_viewer.ToolManager.switch2choosedItem)
        # 将选中标注的位置传送出去，将该位置设置为视图的中心点
        self.slide_viewer.ToolManager.switch2choosedItemSignal.connect(self.slide_viewer.switch2annotation)
        # 将当前的downsample传给ToolManager，用于删除上一个激活的item并重画，再重画当前激活的item
        self.slide_viewer.reactivateItemSignal.connect(self.slide_viewer.ToolManager.reactivateItem)
        # 修改标注类型
        self.annotation.changeAnnotaionSignal.connect(self.slide_viewer.ToolManager.changeAnnotation)
        # 删除标注
        self.annotation.deleteAnnotationSignal.connect(self.slide_viewer.ToolManager.deleteAnnotation)
        # 清除所有标注时，将ToolManager中的self.Annotations清除
        self.annotation.clearAnnotationSignal.connect(self.slide_viewer.ToolManager.clearAnnotations)
        # 清除所有标注时重新画整个视图
        self.slide_viewer.ToolManager.clearViewSignal.connect(self.slide_viewer.reshowView)
        # 将导入的标注与ToolManager同步
        self.annotation.syncAnnotationSignal.connect(self.slide_viewer.ToolManager.syncAnnotation)
        # 将导入的标注显示出来
        self.annotation.showAnnotationSignal.connect(self.slide_viewer.loadAllAnnotation)
        # 将修改的标注坐标信息转递给Annotation
        self.slide_viewer.ToolManager.sendModifiedAnnotationSignal.connect(self.annotation.modifyAnnotation)

        """诊断模式的信号"""
        # 载入诊断结果信号
        self.diagnose.loadDiagnoseSignal.connect(self.slide_viewer.load_diagnose)
        # 开关热图信号
        self.diagnose.showHeatmap_btn.toggled.connect(self.slide_viewer.show_or_close_diagnose_heatmap)
        # 发送诊断框到slideviewer中用于显示
        self.diagnose.sendDiagnoseRectSignal.connect(self.slide_viewer.receiveDiagnoseRect)
        # 点击诊断框，跳转到对应视图
        self.diagnose.sendDiagnoseRectIdxSignal.connect(self.slide_viewer.move2DiagnoseRect)

        """肿瘤微环境信号"""
        self.microenv.loadMicroenvSignal.connect(self.slide_viewer.loadMicroenv)
        self.slide_viewer.sendNucleiNumMicroenvSignal.connect(self.microenv.setNucleiText)
        # 载入结果后，初始化设置要显示的组织轮廓类型
        self.slide_viewer.sendRegionShowTypeMicroenvSignal.connect(self.microenv.showRegionType_Combox.setChecked)
        # 人为选择要显示的组织轮廓类型
        self.microenv.showRegionType_Combox.selectionChangedSignal.connect(self.slide_viewer.update_show_region_types_microenv)
        # 载入结果后，初始化设置要不要显示热图，组织区域，细胞核分割
        self.slide_viewer.sendShowMicroenvSignal.connect(self.microenv.showCombox.setChecked)
        # 人为选择要显示热图，组织轮廓，细胞核分割轮廓
        self.microenv.showCombox.selectionChangedSignal.connect(self.slide_viewer.update_microenv_show)
        # 载入结果后，初始化设置要不要显示表皮细胞，淋巴细胞
        self.slide_viewer.sendNucleiShowTypeMicroenvSignal.connect(self.microenv.showNucleiType_Combox.setChecked)
        # 人为选择要显示表皮细胞，淋巴细胞
        self.microenv.showNucleiType_Combox.selectionChangedSignal.connect(self.slide_viewer.update_show_nuclei_types_microenv)
        # 要显示层级结构还是区域mask
        self.microenv.show_hierarchy_mask_checkbox.stateChanged.connect(self.slide_viewer.change_hierarchy_mask_and_region_mask)

        """PD-L1信号"""
        self.pdl1.loadPDL1Signal.connect(self.slide_viewer.loadPDL1)
        # 显示细胞核个数信息
        self.slide_viewer.sendNucleiNumPDL1Signal.connect(self.pdl1.setNucleiText)
        # 载入结果后，初始化设置要显示的组织轮廓类型
        self.slide_viewer.sendRegionShowTypePDL1Signal.connect(self.pdl1.showRegionType_Combox.setChecked)
        # 人为选择要显示的组织轮廓类型
        self.pdl1.showRegionType_Combox.selectionChangedSignal.connect(self.slide_viewer.update_show_region_types_pdl1)
        # 载入结果后，初始化设置要不要显示热图，组织区域，细胞核分割
        self.slide_viewer.sendShowPDL1Signal.connect(self.pdl1.showCombox.setChecked)
        # 人为选择要显示热图，组织轮廓，细胞核分割轮廓
        self.pdl1.showCombox.selectionChangedSignal.connect(self.slide_viewer.update_pdl1_show)
        # 载入结果后，初始化设置要不要显示表皮细胞，淋巴细胞
        self.slide_viewer.sendNucleiShowTypePDL1Signal.connect(self.pdl1.showNucleiType_Combox.setChecked)
        # 人为选择要显示表皮细胞，淋巴细胞
        self.pdl1.showNucleiType_Combox.selectionChangedSignal.connect(self.slide_viewer.update_show_nuclei_types_pdl1)
        # 全屏模式链接
        self.slide_viewer.full_screen_action.triggered.connect(self.full_screen)

        """多模态模式"""
        self.multimodal.heatmapSignal.connect(self.slide_viewer.update_multimodal_show)

        """标注模式下导入细胞核分割"""
        self.annotation.loadNucleiAnnSignal.connect(self.slide_viewer.loadNuclei)
        self.annotation.saveNucleiAnnSignal.connect(self.slide_viewer.saveNucleiAnn)
        self.annotation.showNucleiAnn_btn.clicked.connect(self.slide_viewer.reverse_nulei)
        self.slide_viewer.reverseBtnSignal.connect(self.annotation.reverse_btn)

        '''载入对比结果'''
        self.microenv.loadPairedWindowSignal.connect(self.load_comparison_slide)
        self.microenv.loadMicroenvComparisonSignal.connect(self.slide_viewer_pair.loadMicroenv)
        self.pdl1.loadPairedWidowSignal.connect(self.load_comparison_slide)
        self.pdl1.loadPDL1ComparisonSignal.connect(self.slide_viewer_pair.loadPDL1)

        self.microenv.show_hierarchy_mask_checkbox.stateChanged.connect(self.slide_viewer_pair.change_hierarchy_mask_and_region_mask)

        """快捷键"""
        self.saveAnnShortcut.activated.connect(self.saveAnnotations)
        self.stopDrawShortcut.activated.connect(self.stopDraw)
        self.deleteAnnShortcut.activated.connect(self.deleteAnnotation)
        self.full_screenShortcut.activated.connect(self.full_screen)


    # 将WSI加载到slide_viewer中
    def load_slide(self, slide_path):
        self.slide_viewer.load_slide(slide_path)
        self.annotation.set_slide_path(slide_path)
        self.diagnose.set_slide_path(slide_path)
        self.microenv.set_slide_path(slide_path)
        self.pdl1.set_slide_path(slide_path)
        self.multimodal.set_slide_path(slide_path)

    # TODO:将WSI加载到slide_viewer中
    def load_comparison_slide(self, slide_path):
        """
        :param slide_path:
        :param mode: mode为1，则为微环境，mode为2，则为pdl1
        :return:
        """
        if not hasattr(self.slide_viewer_pair, "TileLoader"):
            self.slide_viewer_pair.load_slide(slide_path)
            self.splitter_viewer.widget(1).show()

        '''对比窗口加载结果链接'''
        # 载入结果后，初始化设置要显示的组织轮廓类型
        self.slide_viewer_pair.sendRegionShowTypeMicroenvSignal.connect(
            self.microenv.showRegionType_Combox.setChecked)
        # 人为选择要显示的组织轮廓类型
        self.microenv.showRegionType_Combox.selectionChangedSignal.connect(
            self.slide_viewer_pair.update_show_region_types_microenv)
        # 载入结果后，初始化设置要不要显示热图，组织区域，细胞核分割
        self.slide_viewer_pair.sendShowMicroenvSignal.connect(self.microenv.showCombox.setChecked)
        # 人为选择要显示热图，组织轮廓，细胞核分割轮廓
        self.microenv.showCombox.selectionChangedSignal.connect(self.slide_viewer_pair.update_microenv_show)
        # 载入结果后，初始化设置要不要显示表皮细胞，淋巴细胞
        self.slide_viewer_pair.sendNucleiShowTypeMicroenvSignal.connect(
            self.microenv.showNucleiType_Combox.setChecked)
        # 人为选择要显示表皮细胞，淋巴细胞
        self.microenv.showNucleiType_Combox.selectionChangedSignal.connect(
            self.slide_viewer_pair.update_show_nuclei_types_microenv)

        # 载入结果后，初始化设置要显示的组织轮廓类型
        self.slide_viewer_pair.sendRegionShowTypePDL1Signal.connect(self.pdl1.showRegionType_Combox.setChecked)
        # 人为选择要显示的组织轮廓类型
        self.pdl1.showRegionType_Combox.selectionChangedSignal.connect(
            self.slide_viewer_pair.update_show_region_types_pdl1)
        # 载入结果后，初始化设置要不要显示热图，组织区域，细胞核分割
        self.slide_viewer_pair.sendShowPDL1Signal.connect(self.pdl1.showCombox.setChecked)
        # 人为选择要显示热图，组织轮廓，细胞核分割轮廓
        self.pdl1.showCombox.selectionChangedSignal.connect(self.slide_viewer_pair.update_pdl1_show)
        # 载入结果后，初始化设置要不要显示表皮细胞，淋巴细胞
        self.slide_viewer_pair.sendNucleiShowTypePDL1Signal.connect(self.pdl1.showNucleiType_Combox.setChecked)
        # 人为选择要显示表皮细胞，淋巴细胞
        self.pdl1.showNucleiType_Combox.selectionChangedSignal.connect(
            self.slide_viewer_pair.update_show_nuclei_types_pdl1)

        # 将slide_viewer_pair的colorspace与主窗口对齐
        self.slide_viewer_pair.TileLoader.change_colorspace(self.slide_viewer.TileLoader.colorspace)

        registration = self.slide_viewer.Registration
        transform_matrix = np.array([[1, 0, 0],
                                     [0, 1, 0],
                                     [0, 0, 1]])
        self.slide_viewer.init_Registration(transform_matrix, Registration=True)
        self.slide_viewer_pair.init_Registration(np.linalg.inv(transform_matrix), Registration=True)
        if registration is False:
            self.slide_viewer.moveTogetherSignal.connect(self.slide_viewer_pair.move_together)
            self.slide_viewer_pair.moveTogetherSignal.connect(self.slide_viewer.move_together)
            self.slide_viewer.scaleTogetherSignal.connect(self.slide_viewer_pair.scale_together)
            self.slide_viewer_pair.scaleTogetherSignal.connect(self.slide_viewer.scale_together)
            self.slide_viewer_pair.receive_match(*self.slide_viewer.send_match())
            self.slide_viewer.pairMouseSignal.connect(self.slide_viewer_pair.draw_mouse)
            self.slide_viewer_pair.pairMouseSignal.connect(self.slide_viewer.draw_mouse)
            self.slide_viewer.clearMouseSignal.connect(self.slide_viewer_pair.remove_mouse)
            self.slide_viewer_pair.clearMouseSignal.connect(self.slide_viewer.remove_mouse)

    # 将配对窗口与主窗口配对上
    def hook_slide_viewers(self):
        # 如果载入了对比结果
        if hasattr(self.slide_viewer_pair, "TileLoader"):
            if not self.splitter_viewer.widget(1).isVisible():
                self.splitter_viewer.widget(1).show()
            dialog = RegistrationDialog()
            if dialog.exec_() == QDialog.Accepted:
                # 如果已配准就取消配准
                if self.slide_viewer.Registration:
                    self.cancel_paired()
                if dialog.get_flag() == 2:
                    transform_matrix = np.array([[1, 0, 0],
                                                 [0, 1, 0],
                                                 [0, 0, 1]])
                elif dialog.get_flag() == 3:
                    options = QFileDialog.Options()
                    path, _ = QFileDialog.getOpenFileName(self, "选择配准矩阵", f"{constants.cache_path}", "*(*.npy)", options=options)
                    if path == '' or not os.path.exists(path): return
                    transform_matrix = np.load(path)
                    transform_matrix = np.linalg.inv(transform_matrix)
                elif dialog.get_flag() == 1:
                    # 设置为标注模式，不可更改
                    self.lockModeSignal.emit(True)
                    # 设置slide_viewer开启标点模式
                    self.slide_viewer.ToolManager.set_registration_flag(True)
                    self.slide_viewer_pair.ToolManager.set_registration_flag(True)
                    while True:
                        tip_dialog = RegistrationTipDialog()
                        tip_dialog.setWindowFlag(Qt.WindowStaysOnTopHint, True)
                        tip_dialog.show()
                        reply = tip_dialog.exec_()
                        if reply == QDialog.Accepted:
                            points1 = self.slide_viewer.ToolManager.draw_point.get_registration_points()
                            points2 = self.slide_viewer_pair.ToolManager.draw_point.get_registration_points()
                            if len(points1) < 4 or len(points2) < 4:
                                QMessageBox.warning(self, "警告", "要求至少在图中各选择4个点位！")
                            elif len(points1) != len(points2):
                                if len(points1) < len(points2):
                                    QMessageBox.warning(self, "警告", f"请在左边再选{len(points2)-len(points1)}个点")
                                else:
                                    QMessageBox.warning(self, "警告", f"请在右边再选{len(points1) - len(points2)}个点")
                            else:
                                # 计算仿射变换矩阵
                                points1 = np.array(points1)
                                points2 = np.array(points2)
                                transform_matrix = estimate_transform('affine', points2, points1)
                                print("point1", points1)
                                print("point2", points2)
                                print("transform matrix", transform_matrix)
                                break
                        else:
                            break
                    # 打开模式切换开关
                    self.lockModeSignal.emit(False)
                    # 设置slide_viewer关闭标点模式
                    self.slide_viewer.ToolManager.set_registration_flag(False)
                    self.slide_viewer_pair.ToolManager.set_registration_flag(False)
                    if reply != QDialog.Accepted:
                        return
            else:
                return
            self.slide_viewer.init_Registration(np.linalg.inv(transform_matrix), Registration=True)
            self.slide_viewer_pair.init_Registration(transform_matrix, Registration=True)
            self.slide_viewer.moveTogetherSignal.connect(self.slide_viewer_pair.move_together)
            self.slide_viewer_pair.moveTogetherSignal.connect(self.slide_viewer.move_together)
            self.slide_viewer.scaleTogetherSignal.connect(self.slide_viewer_pair.scale_together)
            self.slide_viewer_pair.scaleTogetherSignal.connect(self.slide_viewer.scale_together)
            self.slide_viewer_pair.receive_match(*self.slide_viewer.send_match())
            self.slide_viewer.pairMouseSignal.connect(self.slide_viewer_pair.draw_mouse)
            self.slide_viewer_pair.pairMouseSignal.connect(self.slide_viewer.draw_mouse)
            self.slide_viewer.clearMouseSignal.connect(self.slide_viewer_pair.remove_mouse)
            self.slide_viewer_pair.clearMouseSignal.connect(self.slide_viewer.remove_mouse)

            info_dialog = QMessageBox()
            info_dialog.setWindowTitle("仿射变换矩阵")
            info_dialog.setText(f"图像配准成功\n仿射变换矩阵为:\n{np.linalg.inv(transform_matrix)}")
            info_dialog.exec_()
            slide_name = os.path.splitext(os.path.basename(self.slide_viewer.slide_helper.slide_path))[0]
            np.save(f"{constants.cache_path}/{slide_name}.npy", np.linalg.inv(transform_matrix))

        else:
            QMessageBox.warning(self, "警告", "没有载入同步窗口！")

    # 取消同步的配对关系
    def cancel_paired(self):
        # 如果载入了对比结果
        if hasattr(self.slide_viewer_pair, "TileLoader"):
            # if not self.splitter_viewer.widget(1).isVisible():
            #     self.splitter_viewer.widget(1).show()
            if self.slide_viewer.Registration:
                self.slide_viewer.init_Registration(None, Registration=False)
                self.slide_viewer_pair.init_Registration(None, Registration=False)
                self.slide_viewer.moveTogetherSignal.disconnect(self.slide_viewer_pair.move_together)
                self.slide_viewer_pair.moveTogetherSignal.disconnect(self.slide_viewer.move_together)
                self.slide_viewer.scaleTogetherSignal.disconnect(self.slide_viewer_pair.scale_together)
                self.slide_viewer_pair.scaleTogetherSignal.disconnect(self.slide_viewer.scale_together)
                self.slide_viewer.pairMouseSignal.disconnect(self.slide_viewer_pair.draw_mouse)
                self.slide_viewer_pair.pairMouseSignal.disconnect(self.slide_viewer.draw_mouse)
                self.slide_viewer.clearMouseSignal.disconnect(self.slide_viewer_pair.remove_mouse)
                self.slide_viewer_pair.clearMouseSignal.disconnect(self.slide_viewer.remove_mouse)
            else:
                QMessageBox.warning(self, "提示", "图像没有进行配准！")

    # 快捷键保存标注
    def saveAnnotations(self):
        if hasattr(self, 'annotation'):
            # 如果当前激活的是标注模式
            if self.splitter.widget(0).isVisible():
                self.annotation.saveAnnotations()

    # 快捷键--停止当前标注
    def stopDraw(self):
        if hasattr(self, 'annotation'):
            # 如果时标注模式
            if self.splitter.widget(0).isVisible():
                self.slide_viewer.ToolManager.cancel_drawing()

    def full_screen(self):
        try:
            if hasattr(self, "slide_viewer") and self.isActiveWindow():
                if self.full_screen_flag:
                    # 恢复正常屏幕
                    self.setWindowFlags(Qt.SubWindow)
                    self.showNormal()
                    self.showMaximized()
                    self.full_screen_flag = False
                else:
                    # 全屏
                    # # 获取鼠标的当前位置
                    cursor = QCursor()
                    cursor_pos = cursor.pos()
                    # 获取包含鼠标位置的屏幕
                    screen = QDesktopWidget().screenNumber(cursor_pos)
                    screen_geometry = QDesktopWidget().screenGeometry(screen)
                    # 将窗口设置为包含鼠标位置的屏幕的工作区域
                    self.setGeometry(screen_geometry)
                    self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
                    self.showFullScreen()
                    self.full_screen_flag = True
        except Exception as e:
            print(str(e))

    # 快捷键--删除选中标注
    def deleteAnnotation(self):
        if hasattr(self, 'annotation'):
            # 如果时标注模式
            if self.splitter.widget(0).isVisible():
                self.annotation.deleteAnnotation()

    # 关闭窗口的时候保存标注
    def closeEvent(self, event):
        if hasattr(self, 'annotation'):
            if self.annotation.Annotations:
                if not hasattr(self.annotation, 'slide_path'):
                    text = ''
                else:
                    text = os.path.basename(self.annotation.slide_path)
                dialog = CloseDialog(f"是否要保存{text}标注？")
                if dialog.exec_() == QDialog.Accepted:
                    if dialog.text == '保存':
                        self.annotation.saveAnnotations()
                    else:
                        event.accept()
                else:
                    event.ignore()
                    return
        self.slide_viewer.closeEvent()
        self.slide_viewer_pair.closeEvent()
        return


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = SlideWindow()
    window.show()
    sys.exit(app.exec_())

