import os

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QKeySequence
from window.slide_window import *
from PyQt5.QtCore import Qt
from window.slide_window.utils.AffirmDialog import CloseDialog

class SlideWindow(QFrame):
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

    def init_UI(self):
        main_layout = QVBoxLayout(self)
        self.slide_viewer = SlideViewer()
        self.slide_viewer_pair = SlideViewer(paired=True)
        self.annotation = AnnotationWidget()
        self.diagnose = DiagnoseWidget()
        self.microenv = MicroenvWidget()
        self.pdl1 = PDL1Widget()

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
        self.splitter.addWidget(self.splitter_viewer)
        self.splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.splitter.setSizes([300, 300, 300, 300, 1000])
        self.splitter_viewer.setSizes([1, 1])
        for i in range(1, 4):
            self.splitter.widget(i).hide()
        self.splitter_viewer.widget(1).hide()

        main_layout.addWidget(self.splitter)

    # 初始化快捷键
    def init_shortcut(self):
        self.saveAnnShortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.stopDrawShortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.deleteAnnShortcut = QShortcut(QKeySequence(Qt.Key_Delete), self)

    # 连接信号与槽
    def connectSignalSlot(self):
        """标注模式的信号"""
        # 切换模式时，将ToolManager中的标志位切换了，实现工具的切换
        self.annotation.toolChangeSignal.connect(self.slide_viewer.ToolManager.set_annotation_mode)
        # 切换颜色，将ToolManager中的颜色与类型切换了
        self.annotation.annotationTypeChooseSignal.connect(self.slide_viewer.ToolManager.set_AnnotationColor)
        # 绘制完成标注后，将标注的内容添加到annotaionTree中
        self.slide_viewer.ToolManager.sendAnnotationSignal.connect(self.annotation.addAnnotation)
        # 点击标注栏中的item，获取该标注在视图中的位置
        self.annotation.updateChoosedItemSignal.connect(self.slide_viewer.ToolManager.switch2choosedItem)
        # 将选中标注的位置传送出去，将该位置设置为视图的中心点
        self.slide_viewer.ToolManager.switch2choosedItemSignal.connect(self.slide_viewer.switchWindow)
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

        """标注模式下导入细胞核分割"""
        self.annotation.loadNucleiAnnSignal.connect(self.slide_viewer.loadNuclei)
        self.annotation.saveNucleiAnnSignal.connect(self.slide_viewer.saveNucleiAnn)
        self.annotation.showNucleiAnn_btn.clicked.connect(self.slide_viewer.reverse_nulei)
        self.slide_viewer.reverseBtnSignal.connect(self.annotation.reverse_btn)

        """加载对比结果"""
        # 同步功能开启时，设置为移动模式
        self.slide_viewer.setMoveModeSignal.connect(self.annotation.set_move_mode)
        self.microenv.loadPairedWindowSignal.connect(self.load_slide_pair)
        self.microenv.loadMicroenvComparisonSignal.connect(self.slide_viewer_pair.loadMicroenv)
        self.pdl1.loadPairedWidowSignal.connect(self.load_slide_pair)
        self.pdl1.loadPDL1ComparisonSignal.connect(self.slide_viewer_pair.loadPDL1)
        self.microenv.show_hierarchy_mask_checkbox.stateChanged.connect(self.slide_viewer_pair.change_hierarchy_mask_and_region_mask)

        """快捷键"""
        self.saveAnnShortcut.activated.connect(self.saveAnnotations)
        self.stopDrawShortcut.activated.connect(self.stopDraw)
        self.deleteAnnShortcut.activated.connect(self.deleteAnnotation)


    # 将WSI加载到slide_viewer中
    def load_slide(self, slide_path):
        self.slide_viewer.load_slide(slide_path)
        self.annotation.set_slide_path(slide_path)
        self.diagnose.set_slide_path(slide_path)
        self.microenv.set_slide_path(slide_path)
        self.pdl1.set_slide_path(slide_path)

    # 将WSI加载到slide_viewer中
    def load_slide_pair(self, slide_path, mode=1):
        """
        :param slide_path:
        :param mode: mode为1，则为微环境，mode为2，则为pdl1
        :return:
        """
        if not hasattr(self.slide_viewer_pair, 'slide_helper'):
            self.slide_viewer_pair.load_slide(slide_path)
            self.splitter_viewer.widget(1).show()
            self.slide_viewer.synchronousSignal.connect(self.slide_viewer_pair.eventFilter_from_another_window)
            self.slide_viewer_pair.synchronousSignal.connect(self.slide_viewer.eventFilter_from_another_window)
            self.slide_viewer.slider.slider.valueChanged.connect(
                self.slide_viewer_pair.responseSlider_from_another_window)
            self.slide_viewer_pair.slider.slider.valueChanged.connect(
                self.slide_viewer.responseSlider_from_another_window)
            self.slide_viewer.synchronousThumSignal.connect(
                self.slide_viewer_pair.showImageAtThumArea_from_annother_window)
            self.slide_viewer_pair.synchronousThumSignal.connect(
                self.slide_viewer.showImageAtThumArea_from_annother_window)
        else:
            if self.slide_viewer_pair.slide_helper.slide_path != slide_path:
                self.slide_viewer_pair.load_slide(slide_path)
                self.splitter_viewer.widget(1).show()
                self.slide_viewer.synchronousSignal.connect(self.slide_viewer_pair.eventFilter_from_another_window)
                self.slide_viewer_pair.synchronousSignal.connect(self.slide_viewer.eventFilter_from_another_window)
                self.slide_viewer.slider.slider.valueChanged.connect(
                    self.slide_viewer_pair.responseSlider_from_another_window)
                self.slide_viewer_pair.slider.slider.valueChanged.connect(
                    self.slide_viewer.responseSlider_from_another_window)
                self.slide_viewer.synchronousThumSignal.connect(
                    self.slide_viewer_pair.showImageAtThumArea_from_annother_window)
                self.slide_viewer_pair.synchronousThumSignal.connect(
                    self.slide_viewer.showImageAtThumArea_from_annother_window)
            self.splitter_viewer.widget(1).show()

        # 连接同步信号
        self.slide_viewer.init_position()
        self.slide_viewer_pair.init_position()

        if mode == 1:
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
        elif mode == 2:
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

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = SlideWindow()
    window.show()
    sys.exit(app.exec_())

