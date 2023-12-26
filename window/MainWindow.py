import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon, QColor

import constants
from function import *
from window.FileWatcher import FileWatcher
from window.slide_window import SlideWindow
from window.UI.UI_mainwindow import Ui_MainWindow
from window import StatusBar
from window.slide_window.utils.colorspace_choose_Dialog import ColorSpaceDialog, Channel_Dialog


class MainWindow(QMainWindow, Ui_MainWindow):
    RecentFilePath = os.path.join(constants.cache_path, "recent_file.json")
    FixedRectSizePath = os.path.join(constants.cache_path, "FixedRectSize.json")
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.init_UI()
        self.connectActionFunc()
        self.init_attr()
        self.set_recent_file()
        self.setEnable()

        # 打开文件监控窗口
        self.open_file_watcher()

    def init_UI(self):
        self.setupUi(self)
        self.setStyleSheet("QMenuBar{font-family:宋体; font: bold 14px;font-weight:400}")
        self.setWindowTitle('智能病理辅助诊断平台(Computational Pathology Platform)')

        icon = QIcon('logo/logo.png')
        self.setWindowIcon(icon)
        self.setCentralWidget(self.mdiArea)
        # 设置控件的焦点策略
        self.setFocusPolicy(Qt.ClickFocus)
        # 设置多文档界面的视图模式为选项卡式视图
        self.mdiArea.setViewMode(QMdiArea.TabbedView)
        # 设置选项卡是否可关闭
        self.mdiArea.setTabsClosable(True)
        # 设置选项卡是否可移动
        self.mdiArea.setTabsMovable(True)

        # 初始化状态栏
        self.statusbar = StatusBar(self.mdiArea)
        self.setStatusBar(self.statusbar)
        self.action_enabel(False)

        # 全屏显示
        self.showMaximized()
        self.set_style()

    # 将动作与功能代码连接
    def connectActionFunc(self):
        self.open_slide_action.triggered.connect(self.open_slide_window)
        self.open_file_manager_action.triggered.connect(self.open_file_watcher)
        self.change_file_manager_action.triggered.connect(self.change_file_watcher_dir)
        self.open_paired_action.triggered.connect(self.open_paired_slide_window)
        self.open_paired_win_action.triggered.connect(self.show_paired_slide_window)
        self.close_paired_win_action.triggered.connect(self.hide_paired_slide_window)
        self.synchronization_action.triggered.connect(self.Registration_match)
        self.cancel_synchronization_action.triggered.connect(self.cancel_registration_match)

        self.annotation_action.triggered.connect(self.onTriggered)
        self.diagnose_action.triggered.connect(self.onTriggered)
        self.microenv_action.triggered.connect(self.onTriggered)
        self.pdl1_action.triggered.connect(self.onTriggered)
        self.multimodal_action.triggered.connect(self.onTriggered)
        self.move_action.triggered.connect(self.onTriggered)
        self.fixed_rect_action.triggered.connect(self.onTriggered)
        self.rect_action.triggered.connect(self.onTriggered)
        self.polygon_action.triggered.connect(self.onTriggered)
        self.measure_tool_action.triggered.connect(self.onTriggered)
        self.modify_action.triggered.connect(self.onTriggered)

        self.annotation_action.triggered.connect(lambda:  self.mode_switching(0))
        self.diagnose_action.triggered.connect(lambda: self.mode_switching(1))
        self.microenv_action.triggered.connect(lambda: self.mode_switching(2))
        self.pdl1_action.triggered.connect(lambda: self.mode_switching(3))
        self.multimodal_action.triggered.connect(lambda : self.mode_switching(4))
        self.move_action.triggered.connect(lambda: self.tools_toggle(1))
        self.fixed_rect_action.triggered.connect(lambda: self.tools_toggle(2))
        self.rect_action.triggered.connect(lambda: self.tools_toggle(3))
        self.polygon_action.triggered.connect(lambda: self.tools_toggle(4))
        self.measure_tool_action.triggered.connect(lambda: self.tools_toggle(5))
        self.modify_action.triggered.connect(lambda: self.tools_toggle(6))
        self.convert_color_space_action.triggered.connect(self.colorspace_transform)

        # 创建一个 QAction 组
        self.mode_group = QActionGroup(self)
        self.mode_group.setExclusive(True)
        self.annotation_action.setActionGroup(self.mode_group)
        self.diagnose_action.setActionGroup(self.mode_group)
        self.microenv_action.setActionGroup(self.mode_group)
        self.pdl1_action.setActionGroup(self.mode_group)
        self.multimodal_action.setActionGroup(self.mode_group)

        tool_group = QActionGroup(self)
        tool_group.setExclusive(True)
        self.move_action.setActionGroup(tool_group)
        self.fixed_rect_action.setActionGroup(tool_group)
        self.rect_action.setActionGroup(tool_group)
        self.polygon_action.setActionGroup(tool_group)
        self.measure_tool_action.setActionGroup(tool_group)
        self.modify_action.setActionGroup(tool_group)

        # 当切换子窗口时，要设置工具栏
        self.mdiArea.subWindowActivated.connect(self.set_window_status)
        # 设置ROI尺寸
        self.rect_resiz_action.triggered.connect(self.setRoiSize)
        # 关闭
        self.quit.triggered.connect(self.close)

    # 初始化变量
    def init_attr(self):
        self.slide_file_dir = './'

    # 设置action使能
    def setEnable(self):
        # self.fill_screen_action.setEnabled(False)
        self.recall_action.setEnabled(False)
        self.shot_screen_action.setEnabled(False)

    # 打开slide window
    def open_slide_window(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "选择WSI文件", self.slide_file_dir,
                                                   "WSI ({});".format(get_file_option()), options=options)
        self.openslide(file_path)

    # 打开文件
    def openslide(self, file_path, mode=None):
        try:
            # 判断文件是否可以打开
            waning_text = judge_slide_path(file_path)
            if waning_text == True:
                self.slide_file_dir = os.path.dirname(file_path)
                slide_window = SlideWindow(file_path)
                slide_window.annotation.AnnotationTypeChangeSignal.connect(self.bindAnnotationColor)
                slide_window.annotation.annotationActionCheckSignal.connect(self.set_color_action_checked)
                slide_window.lockModeSignal.connect(self.lock_mode)
                self.mdiArea.addSubWindow(slide_window)
                slide_window.show()
                slide_window.setWindowTitle(os.path.basename(file_path))
                # 设置工具栏上的图像块的颜色
                slide_window.annotation.set_activate_color_action()
                # 设置工具栏上图像块点击所发出的指令
                self.connect_Annotation_ation()
                self.add_recent_path(file_path)

                # 将菜单栏中的按键连接到Slideviewer中
                slide_window.slide_viewer.addAction2Menu([self.move_action, self.fixed_rect_action, self.rect_action,
                                                          self.polygon_action, self.measure_tool_action, self.modify_action,
                                                          None, self.annotation_action, self.diagnose_action, self.microenv_action,
                                                          self.pdl1_action, self.multimodal_action, None])
                # 全屏的功能连接
                self.fill_screen_action.triggered.connect(slide_window.full_screen)
                if mode == '诊断':
                    self.diagnose_action.trigger()
                    slide_window.diagnose.loadDiagnoseResults_btn.click()
                # TODO:直接跳转到微环境分析以及PD-L1测量页面
            else:
                if waning_text is None:
                    return
                else:
                    QMessageBox.warning(self, '警告', waning_text)
        except Exception as e:
            QMessageBox.warning(self, '警告', str(e))

    def add_recent_path(self, file_path):
        # 添加到最近文件中
        if file_path in self.recent_file:
            self.recent_file.remove(file_path)
        self.recent_file.insert(0, file_path)
        self.recentFileActions = []
        for file_path in self.recent_file[:20]:
            self.add_recent_file(file_path)
            self.open_recent_slide_menu.clear()
            self.open_recent_slide_menu.addActions(self.recentFileActions)

        with open(self.RecentFilePath, 'w') as f:
            f.write(json.dumps(self.recent_file, indent=2))
            f.close()

    def open_paired_slide_window(self):
        sub_active = self.mdiArea.activeSubWindow()
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "选择WSI文件", self.slide_file_dir,
                                                   "WSI ({});".format(get_file_option()), options=options)
        # 判断文件是否可以打开
        waning_text = judge_slide_path(file_path)
        if waning_text == True:
            self.slide_file_dir = os.path.dirname(file_path)
            slide_viewer_pair = sub_active.widget().slide_viewer_pair
            slide_viewer_pair.load_slide(file_path)
            splitter_viewer = sub_active.widget().splitter_viewer
            splitter_viewer.widget(1).show()
            # 将菜单栏中的按键连接到Slideviewer中
            slide_viewer_pair.addAction2Menu([])
        else:
            if waning_text is None:
                return
            else:
                QMessageBox.warning(self, '警告', waning_text)
        return


    # 如果导入了同步图片，则进行显示
    def show_paired_slide_window(self):
        sub_active = self.mdiArea.activeSubWindow()
        try:
            if hasattr(sub_active.widget(), 'slide_viewer_pair'):
                slide_viewer_pair = sub_active.widget().slide_viewer_pair
                if hasattr(slide_viewer_pair, 'TileLoader'):
                    splitter_viewer = sub_active.widget().splitter_viewer
                    splitter_viewer.widget(1).show()
                else:
                    QMessageBox.warning(self, '警告', "没有载入同步图像")
        except:
            QMessageBox.warning(self, '警告', "没有打开图像子窗口")

    # 如果导入了同步图片，则隐藏同步图片
    def hide_paired_slide_window(self):
        sub_active = self.mdiArea.activeSubWindow()
        try:
            if hasattr(sub_active.widget(), 'slide_viewer_pair'):
                slide_viewer_pair = sub_active.widget().slide_viewer_pair
                if hasattr(slide_viewer_pair, 'TileLoader'):
                    splitter_viewer = sub_active.widget().splitter_viewer
                    splitter_viewer.widget(1).hide()
                else:
                    QMessageBox.warning(self, '警告', "没有载入同步图像")
        except:
            QMessageBox.warning(self, '警告', "没有打开图像子窗口")

    # 设置图像配准
    def Registration_match(self):
        sub_active = self.mdiArea.activeSubWindow()
        # 如果时图像显示窗口
        if hasattr(sub_active.widget(), 'slide_viewer'):
            slide_window = sub_active.widget()
            slide_window.hook_slide_viewers()
        else:
            QMessageBox.warning(self, "警告", "请打开图像！")

    def cancel_registration_match(self):
        sub_active = self.mdiArea.activeSubWindow()
        # 如果时图像显示窗口
        if hasattr(sub_active.widget(), 'slide_viewer'):
            slide_window = sub_active.widget()
            slide_window.cancel_paired()
        else:
            QMessageBox.warning(self, "警告", "请打开图像！")

    # 打开文件监控目录
    def open_file_watcher(self):           # 链接open_file_manager_action
        # 打开文件监控窗口
        if hasattr(self, 'file_watcher'):
            self.mdiArea.setActiveSubWindow(self.file_watcher.parent())
            return
        self.file_watcher = FileWatcher('')
        self.file_watcher.setWindowTitle('文件监控窗口')
        self.mdiArea.addSubWindow(self.file_watcher)
        self.file_watcher.closeSignal.connect(self.del_fileWatcher)
        self.file_watcher.openslideSignal.connect(self.openslide)
        self.batch_process_action.triggered.connect(self.file_watcher.batch_process)
        self.stop_batch_process_action.triggered.connect(self.file_watcher.stop_batch_process)
        self.file_watcher.show()

    # 更改文件监控目录
    def change_file_watcher_dir(self):    # 链接change_file_manager_action
        file_dir_path = QFileDialog.getExistingDirectory(self, '选择监控目录', './')
        if os.path.exists(file_dir_path):
            if hasattr(self, 'file_watcher'):
                if hasattr(self.file_watcher, 't'):
                    if self.file_watcher.t.isRunning():
                        QMessageBox.warning(self, '警告', '正在批处理，无法更换目录！')
                        return
                self.file_watcher.set_path(file_dir_path)
            else:
                self.open_file_watcher()
                self.file_watcher.set_path(file_dir_path)
            saveFileWatcherDir(file_dir_path)

    # 关闭filewatcher时将其属性删除,否则再次大概文件监控窗口会出错
    def del_fileWatcher(self):  # 链接file_watcher.closeSignal
        del self.file_watcher

    # 查看当前属于什么模式
    def get_visible_widget(self, splitter: QSplitter):
        for i in range(splitter.count()):
            if i == splitter.count() - 1:
                return None
            if splitter.widget(i).isVisible():
                return i

    # 模式切换
    # 输入为0~3的值，分别表示标注，诊断，微环境，PD-L1
    def mode_switching(self, mode2switch):
        sub_active = self.mdiArea.activeSubWindow()
        try:
            if hasattr(sub_active.widget(), 'splitter'):
                splitter = sub_active.widget().splitter
                current_mode = self.get_visible_widget(splitter)
                if current_mode is None:
                    return
                if current_mode != mode2switch:
                    splitter.widget(mode2switch).show()
                    splitter.widget(current_mode).hide()
                    # 切换成移动模式
                    sub_active.widget().slide_viewer.ToolManager.TOOL_FLAG = 1
                    self.tools_toggle(1)
                    # 重新绘制当前窗口
                    sub_active.widget().slide_viewer.reshowView()
                    sub_active.widget().slide_viewer_pair.reshowView()

                    # 将诊断模式显示的热图关闭，诊断框删去
                    if current_mode == 1:
                        sub_active.widget().diagnose.showHeatmap_btn.setChecked(False)
                        sub_active.widget().slide_viewer.removeDiagnoseRect()
                    elif current_mode == 2 or current_mode == 3:
                        sub_active.widget().slide_viewer.show_or_close_heatmap(None, None, False)
                        sub_active.widget().slide_viewer_pair.show_or_close_heatmap(None, None, False)
                    elif current_mode == 4:
                        sub_active.widget().slide_viewer.update_multimodal_show(None, None, False)
                        sub_active.widget().slide_viewer_pair.update_multimodal_show(None, None, False)

                    # TODO：设置显示标志位
                    if mode2switch == 0:
                        sub_active.widget().slide_viewer.SHOW_FLAG = 0
                        sub_active.widget().slide_viewer_pair.SHOW_FLAG = 0
                        # 重新绘制标注
                        sub_active.widget().slide_viewer.loadAllAnnotation()
                    elif mode2switch == 1:
                        sub_active.widget().slide_viewer.SHOW_FLAG = 1
                        sub_active.widget().slide_viewer_pair.SHOW_FLAG = 1
                        # 重新绘制诊断框
                        sub_active.widget().slide_viewer.redrawDiagnoseRect()
                    elif mode2switch == 2:
                        sub_active.widget().slide_viewer.SHOW_FLAG = 2
                        sub_active.widget().slide_viewer_pair.SHOW_FLAG = 2
                        # 重新绘制微环境分析
                        sub_active.widget().slide_viewer.update_microenv_show(sub_active.widget().slide_viewer.show_list_microenv)
                        sub_active.widget().slide_viewer_pair.update_microenv_show(sub_active.widget().slide_viewer_pair.show_list_microenv)
                    elif mode2switch == 3:
                        sub_active.widget().slide_viewer.SHOW_FLAG = 3
                        sub_active.widget().slide_viewer_pair.SHOW_FLAG = 3
                        # 重新绘PDL1
                        sub_active.widget().slide_viewer.update_pdl1_show(sub_active.widget().slide_viewer.show_list_pdl1)
                        sub_active.widget().slide_viewer_pair.update_pdl1_show(sub_active.widget().slide_viewer_pair.show_list_pdl1)
                    elif mode2switch == 4:
                        sub_active.widget().slide_viewer.SHOW_FLAG = 4
                        sub_active.widget().slide_viewer_pair.SHOW_FLAG = 4
                    if mode2switch != 0:
                        sub_active.widget().slide_viewer.setCursor(Qt.ArrowCursor)
                        self.annotation_action_enable(False)
                    else:
                        self.annotation_action_enable(True)
        except:
            QMessageBox.warning(self, '警告', "没有打开图像子窗口")

    # 当手动进行配准时，要将模式切换到标注模式，同时不能够更换模式，将标注工具切换成移动工具
    def lock_mode(self, lock=True):
        if lock:
            # 切换为标注模式
            self.mode_switching(0)
            # 切换为移动模式
            self.tools_toggle(1)
            # 锁住模式切换
            self.action_enabel(False)
        else:
            self.action_enabel(True)

    def colorspace_transform(self):
        sub_active = self.mdiArea.activeSubWindow()
        if hasattr(sub_active.widget(), 'slide_viewer'):
            slide_viewer = sub_active.widget().slide_viewer
            if hasattr(slide_viewer, "slide_helper"):
                is_fluorescene = slide_viewer.slide_helper.is_fluorescene
                num_markers = 0 if is_fluorescene is False else slide_viewer.slide_helper.num_markers
                if num_markers == 0:
                    colorspace_dialog = ColorSpaceDialog(slide_viewer.TileLoader.colorspace)
                else:
                    colorspace_dialog = Channel_Dialog(slide_viewer.TileLoader.colorspace, num_markers, slide_viewer.slide_helper.fluorescene_color_list, slide_viewer.TileLoader.channel_intensities)
                if colorspace_dialog.exec_() == QDialog.Accepted:
                    selected_option, channel_intensities = colorspace_dialog.get_selected_option()
                    if selected_option == []:
                        QMessageBox.warning(self, '警告', "至少选择一个颜色通道！")
                        return
                    print("选择的颜色空间:", selected_option)
                    slide_viewer.TileLoader.change_colorspace(selected_option, channel_intensities)

    # 标注工具切换
    def tools_toggle(self, mode2switch):
        sub_active = self.mdiArea.activeSubWindow()
        try:
            if hasattr(sub_active.widget(), 'annotation'):
                # TODO：判断当前如果不是标注模式，则不能进行标注工具的切换
                if self.get_visible_widget(sub_active.widget().splitter) == 0:
                    annotation = sub_active.widget().annotation
                    annotation.set_annotation_mode(mode2switch)
                    # 如果标志位不为move，则将slide_viewer中的move_allow_flag设置为Flase
                    # 对于同步窗口move_allow_flag永远都是True
                    slide_viewer = sub_active.widget().slide_viewer
                    if mode2switch != 1:
                        slide_viewer.set_Move_Allow(False)
                    else:
                        slide_viewer.set_Move_Allow(True)
                    if mode2switch == 1:
                        slide_viewer.setCursor(Qt.ArrowCursor)
                    elif mode2switch == 6:
                        slide_viewer.setCursor(Qt.PointingHandCursor)
                    else:
                        slide_viewer.setCursor(Qt.CrossCursor)

                else:
                    self.move_action.setChecked(True)
                    slide_viewer = sub_active.widget().slide_viewer
                    slide_viewer.set_Move_Allow(True)
        except:
            QMessageBox.warning(self, '警告', "没有打开图像子窗口")

    # 接触信号与函数的连接
    def disconnect_action_signal(self, action: QAction):
        action.triggered.disconnect()

    # 进行链接：点击状态栏中的图像块，设置标注的颜色与类型
    def connect_Annotation_ation(self):
        # 解除activate_color_action与之前绑定的函数的链接
        self.disconnect_action_signal(self.activate_color_action1)
        self.disconnect_action_signal(self.activate_color_action2)
        self.disconnect_action_signal(self.activate_color_action3)
        self.disconnect_action_signal(self.activate_color_action4)
        sub_active = self.mdiArea.activeSubWindow()
        try:
            if hasattr(sub_active.widget(), 'annotation'):
                annotation = sub_active.widget().annotation
                self.activate_color_action1.triggered.connect(lambda: annotation.set_AnnotationColor(0))
                self.activate_color_action2.triggered.connect(lambda: annotation.set_AnnotationColor(1))
                self.activate_color_action3.triggered.connect(lambda: annotation.set_AnnotationColor(2))
                self.activate_color_action4.triggered.connect(lambda: annotation.set_AnnotationColor(3))

                # 连接信号，选择标注时，同样会激活菜单栏中的颜色块
                self.set_color_action_checked(annotation.annotation_flag)

        except:
            QMessageBox.warning(self, '警告', "没有打开图像子窗口")

    # 改变工具栏中标注颜色的图块颜色
    def bindAnnotationColor(self, annotationType: dict):
        for idx, (key, value) in enumerate(annotationType.items()):
            if idx > 3:
                return
            pixmap = QPixmap(20, 20)
            color = QColor(*value)
            pixmap.fill(color)
            icon = QIcon(pixmap)
            actions = self.toolBar.actions()
            for action in actions:
                if action.text() == f"颜色{idx+1}":
                    action.setIcon(icon)
            self.toolBar.update()

    # 设置选中的模式checked
    def onTriggered(self):
        # 获取触发信号的 QAction 对象
        action = self.sender()
        # 设置 QAction 被选中的状态
        action.setChecked(True)

    # 切换子窗口
    # 当切换子窗口时，把标注工具设置成移动工具，模式与上次切换时保持一致
    def set_window_status(self):
        sub_active = self.mdiArea.activeSubWindow()
        # 如果打开的是并不是图像窗口，那么需要将菜单栏的使能关闭
        try:
            if hasattr(sub_active.widget(), 'slide_viewer'):
                self.action_enabel(True)
            else:
                self.action_enabel(False)
        except:
            print("Main Window 429行")

        try:
            if hasattr(sub_active.widget(), 'slide_viewer'):
                # 设置状态栏中的颜色，并于AnnotationTypeTree中的信息进行链接
                self.bindAnnotationColor(sub_active.widget().annotation.AnnotationTypes)
                self.connect_Annotation_ation()

                # 设置模式，设置为当前模式
                current_mode = self.get_visible_widget(sub_active.widget().splitter)
                action = self.mode_group.actions()[current_mode]
                action.setChecked(True)

                # 设置标注工具,设置为移动模式
                self.tools_toggle(1)
                self.move_action.setChecked(True)
        except:
            print("MainWindow 437 行")

        # 如果激活了文件监控窗口，则打开定时器
        # 如果激活的不是文件监控窗口，则关闭定时器
        try:
            if sub_active.windowTitle() == '文件监控窗口':
                file_watcher = sub_active.window().file_watcher
                file_watcher.start_timer()
            else:
                windows = self.mdiArea.subWindowList()
                for sub_window in windows:
                    # print(sub_window.windowTitle())
                    if sub_window.windowTitle() == '文件监控窗口':
                        file_watcher = sub_window.window().file_watcher
                        file_watcher.stop_timer()
        except:
            print("MainWindow 453 行")

    # TODO: 关闭子窗口时会触发mdiArea.subWindowActivated，要避免这种情况

    # 增加action
    def add_recent_file(self, path, fist=False):
        action = QAction(path)
        action.triggered.connect(lambda: self.openslide(path))
        if fist:
            self.recentFileActions.insert(0, action)
        else:
            self.recentFileActions.append(action)

    # 初始化最近文件
    def set_recent_file(self):
        self.recentFileActions = []
        if os.path.exists(self.RecentFilePath):
            with open(self.RecentFilePath, 'r') as f:
                self.recent_file = json.load(f)[:20]
                f.close()
            for path in self.recent_file:
                self.add_recent_file(path)
                self.open_recent_slide_menu.clear()
                self.open_recent_slide_menu.addActions(self.recentFileActions)
        else:
            self.recent_file = []

    def set_style(self):
        self.setStyleSheet("""* {font-family: 宋体; font-size: 14px;}""")

    def setRoiSize(self):
        from window.slide_window.utils.SizeInputDialog import SizeInputDialog
        dialog = SizeInputDialog()
        if dialog.exec_() == QDialog.Accepted:
            width, height = dialog.get_size()
            if isinstance(width, int) and isinstance(height, int):
                with open(self.FixedRectSizePath, 'w') as f:
                    f.write(json.dumps({"width": width,
                                        "height": height}))
                    f.close()
            else:
                QMessageBox.warning(self, '警告', '输入的数字不是整数')

    # 关闭窗口的时候保存标注
    def closeEvent(self, event):
        for subwindow in self.mdiArea.subWindowList():
            subwindow.closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # app.setAttribute(Qt.AA_EnableHighDpiScaling)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())