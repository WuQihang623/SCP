import json
import os
import sys
import qdarkstyle
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSize
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap, QIcon, QColor

from function import *
from window.FileWatcher import FileWatcher
from window.slide_window import SlideWindow
from window.UI.UI_mainwindow import Ui_MainWindow
from window import StatusBar


class MainWindow(QMainWindow, Ui_MainWindow):
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
        self.setStyleSheet("QMenuBar{font-family:微软雅黑; font: bold 14px;font-weight:400}")
        self.setWindowTitle('智能病理辅助诊断平台（Computational Pathology Platform）')
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

        # TODO：初始化Action的使能

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

        self.annotation_action.triggered.connect(self.onTriggered)
        self.diagnose_action.triggered.connect(self.onTriggered)
        self.microenv_action.triggered.connect(self.onTriggered)
        self.pdl1_action.triggered.connect(self.onTriggered)
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
        self.move_action.triggered.connect(lambda: self.tools_toggle(1))
        self.fixed_rect_action.triggered.connect(lambda: self.tools_toggle(2))
        self.rect_action.triggered.connect(lambda: self.tools_toggle(3))
        self.polygon_action.triggered.connect(lambda: self.tools_toggle(4))
        self.measure_tool_action.triggered.connect(lambda: self.tools_toggle(5))
        self.modify_action.triggered.connect(lambda: self.tools_toggle(6))


        # 创建一个 QAction 组
        self.mode_group = QActionGroup(self)
        self.mode_group.setExclusive(True)
        self.annotation_action.setActionGroup(self.mode_group)
        self.diagnose_action.setActionGroup(self.mode_group)
        self.microenv_action.setActionGroup(self.mode_group)
        self.pdl1_action.setActionGroup(self.mode_group)

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

    # 初始化变量
    def init_attr(self):
        self.slide_file_dir = './'

    # 设置action使能
    def setEnable(self):
        # self.paired_slide_menu.setEnabled(False)
        self.fill_screen_action.setEnabled(False)
        self.quit.setEnabled(False)
        self.recall_action.setEnabled(False)
        self.convert_color_space_action.setEnabled(False)
        # self.microenv_action.setEnabled(False)
        # self.pdl1_action.setEnabled(False)
        self.shot_screen_action.setEnabled(False)


    # 打开slide window
    def open_slide_window(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "选择WSI文件", self.slide_file_dir,
                                                   "WSI ({});".format(get_file_option()), options=options)
        self.openslide(file_path)

    # 打开文件
    def openslide(self, file_path, mode=None):
        # 判断文件是否可以打开
        waning_text = judge_slide_path(file_path)
        if waning_text == True:
            self.slide_file_dir = os.path.dirname(file_path)
            slide_window = SlideWindow(file_path)
            slide_window.annotation.AnnotationTypeChangeSignal.connect(self.bindAnnotationColor)
            self.mdiArea.addSubWindow(slide_window)
            slide_window.show()
            slide_window.setWindowTitle(os.path.basename(file_path))
            # 设置工具栏上的图像块的颜色
            slide_window.annotation.set_activate_color_action()
            # 设置工具栏上图像块点击所发出的指令
            self.set_AnnotationColor()
            self.add_recent_path(file_path)

            if mode == '诊断':
                self.diagnose_action.trigger()
                slide_window.diagnose.loadDiagnoseResults_btn.click()
            # TODO:直接跳转到微环境分析以及PD-L1测量页面

        else:
            if waning_text is None:
                return
            else:
                QMessageBox.warning(self, '警告', waning_text)

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

        os.makedirs('./cache', exist_ok=True)
        with open('./cache/recent_file.json', 'w') as f:
            f.write(json.dumps(self.recent_file, indent=2))
            f.close()

    def open_paired_slide_window(self):
        sub_active = self.mdiArea.activeSubWindow()
        # try:
        if hasattr(sub_active.widget(), 'slide_viewer_pair'):
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
                # sub_active.widget().slide_viewer.synchronousSignal.connect(slide_viewer_pair.eventFilter1)
            else:
                if waning_text is None:
                    return
                else:
                    QMessageBox.warning(self, '警告', waning_text)
            return
        else:
            QMessageBox.warning(self, '警告', "没有打开图像子窗口")

    # 打开同步图片
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

    # 关闭同步图片
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

    # 打开文件监控目录
    def open_file_watcher(self):           # 链接open_file_manager_action
        # 打开文件监控窗口
        if hasattr(self, 'file_watcher'):
            self.mdiArea.setActiveSubWindow(self.file_watcher.parent())
            return
        self.file_watcher = FileWatcher('')
        self.file_watcher.setWindowTitle('文件监控窗口')
        self.mdiArea.addSubWindow(self.file_watcher)
        self.file_watcher.show()
        self.file_watcher.closeSignal.connect(self.del_fileWatcher)
        self.file_watcher.openslideSignal.connect(self.openslide)
        self.batch_process_action.triggered.connect(self.file_watcher.batch_process)
        self.stop_batch_process_action.triggered.connect(self.file_watcher.stop_batch_process)

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
                    elif current_mode >= 2:
                        sub_active.widget().slide_viewer.show_or_close_heatmap(None, None, False)
                        sub_active.widget().slide_viewer_pair.show_or_close_heatmap(None, None, False)

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
                    if mode2switch != 0:
                        sub_active.widget().slide_viewer.setCursor(Qt.ArrowCursor)
        except:
            QMessageBox.warning(self, '警告', "没有打开图像子窗口")

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
    def set_AnnotationColor(self):
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

    # 当切换子窗口时，把标注工具设置成移动工具，模式与上次切换时保持一致
    def set_window_status(self):
        sub_active = self.mdiArea.activeSubWindow()
        try:
            if hasattr(sub_active.widget(), 'slide_viewer'):
                # 设置状态栏中的颜色，并于AnnotationTypeTree中的信息进行链接
                self.bindAnnotationColor(sub_active.widget().annotation.AnnotationTypes)
                self.set_AnnotationColor()

                # 设置模式，设置为当前模式
                current_mode = self.get_visible_widget(sub_active.widget().splitter)
                action = self.mode_group.actions()[current_mode]
                action.setChecked(True)

                # 设置标注工具,设置为移动模式
                self.tools_toggle(1)
                self.move_action.setChecked(True)
        except:
            pass

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
            pass
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
        if os.path.exists('./cache/recent_file.json'):
            with open('./cache/recent_file.json', 'r') as f:
                self.recent_file = json.load(f)[:20]
                f.close()
            for path in self.recent_file:
                self.add_recent_file(path)
                self.open_recent_slide_menu.clear()
                self.open_recent_slide_menu.addActions(self.recentFileActions)
        else:
            self.recent_file = []

    def set_style(self):
        self.setStyleSheet("""* {font-size: 16px;}""")


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