import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon, QColor

import constants
from function import *
from window import StatusBar
from window.FileWatcher import FileWatcher
from window.slide_window import SlideWindow
from window.UI.UI_mainwindow import Ui_MainWindow

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
        self.open_paired_action.triggered.connect(self.openSideViewer)
        self.open_paired_win_action.triggered.connect(self.showSideVierwer)
        self.close_paired_win_action.triggered.connect(self.hideSideViewer)
        self.synchronization_action.triggered.connect(self.Registration_match)
        self.cancel_synchronization_action.triggered.connect(self.cancel_registration_match)

        self.move_action.triggered.connect(self.onTriggered)
        self.fixed_rect_action.triggered.connect(self.onTriggered)
        self.rect_action.triggered.connect(self.onTriggered)
        self.polygon_action.triggered.connect(self.onTriggered)
        self.measure_tool_action.triggered.connect(self.onTriggered)
        self.modify_action.triggered.connect(self.onTriggered)

        self.move_action.triggered.connect(lambda: self.tools_toggle(1))
        self.fixed_rect_action.triggered.connect(lambda: self.tools_toggle(2))
        self.rect_action.triggered.connect(lambda: self.tools_toggle(3))
        self.polygon_action.triggered.connect(lambda: self.tools_toggle(4))
        self.measure_tool_action.triggered.connect(lambda: self.tools_toggle(5))
        self.modify_action.triggered.connect(lambda: self.tools_toggle(6))

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

    def set_recent_file(self):
        """
            初始化最近打开文件
        """
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

    # 设置action使能
    def setEnable(self):
        # self.fill_screen_action.setEnabled(False)
        self.recall_action.setEnabled(False)
        self.shot_screen_action.setEnabled(False)

    def open_slide_window(self):
        """
            打开slide window
        """
        file_path, warning_text = self.selete_path("选择WSI文件")
        if warning_text != True:
            if warning_text is None:
                return
            else:
                QMessageBox.warning(self, '警告', warning_text)
                return
        self.openSlide(file_path)

    def openSlide(self, file_path):
        """
            可以通过文件监控窗口或者菜单栏以及最近文件打开WSI
        """
        try:
            # 判断文件是否可以打开
            warning_text = judge_slide_path(file_path)
            if warning_text != True:
                if warning_text is None:
                    return
                else:
                    QMessageBox.warning(self, '警告', warning_text)
                    return

            self.slide_file_dir = os.path.dirname(file_path)
            slide_window = SlideWindow(file_path)
            slide_window.setWindowTitle(os.path.basename(file_path))
            self.mdiArea.addSubWindow(slide_window)
            slide_window.show()

            # 向最近文件中添加文件
            self.add_recent_path(file_path)

            # TODO: 设置一些标注工具的信号
            slide_window.controller.annotationTypeChooseSignal.connect(self.set_color_action_checked)
            slide_window.controller.updateAnnotationTypeSignal.connect(self.bindAnnotationColor)

            # TODO: 设置工具栏上的图像块的颜色
            self.annotaionColorConnections()
            self.bindAnnotationColor(slide_window.controller.annotationTypeDict)

            # 将菜单栏中的按键连接到Slideviewer中
            slide_window.mainViewer.addAction2Menu([self.move_action, self.fixed_rect_action, self.rect_action,
                                                      self.polygon_action, self.measure_tool_action, self.modify_action, None])
            # TODO:全屏的功能连接
            # self.fill_screen_action.triggered.connect(slide_window.full_screen)

            slide_window.lockMoveModeSignal.connect(self.lock_mode)

        except Exception as e:
            QMessageBox.warning(self, '警告', str(e))

    def openSideViewer(self):
        sub_active = self.mdiArea.activeSubWindow()
        file_path, warning_text = self.selete_path("选择WSI文件")
        if warning_text != True:
            if warning_text is None:
                return
            else:
                QMessageBox.warning(self, '警告', warning_text)
                return

        self.slide_file_dir = os.path.dirname(file_path)
        sub_active.widget().sideViewerLoadSlide(file_path)
        sub_active.widget().hookSlideViewer()

    def selete_path(self, title):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, title, self.slide_file_dir, "WSI ({});".format(get_file_option()), options=options)
        # 判断文件是否可以打开
        warning_text = judge_slide_path(file_path)
        return file_path, warning_text

    def showSideVierwer(self):
        """
            如果导入了同步图片，则进行显示
        """
        sub_active = self.mdiArea.activeSubWindow()
        try:
            if hasattr(sub_active.widget(), 'sideViewer'):
                sideViewer = sub_active.widget().sideViewer
                if hasattr(sideViewer, 'TileLoader'):
                    splitter_viewer = sub_active.widget().splitter_viewer
                    splitter_viewer.widget(1).show()
                else:
                    QMessageBox.warning(self, '警告', "没有载入同步图像")
        except:
            QMessageBox.warning(self, '警告', "没有打开图像子窗口")

    def hideSideViewer(self):
        """
            如果导入了同步图片，则隐藏同步图片
        """
        sub_active = self.mdiArea.activeSubWindow()
        try:
            if hasattr(sub_active.widget(), 'sideViewer'):
                sideViewer = sub_active.widget().sideViewer
                if hasattr(sideViewer, 'TileLoader'):
                    splitter_viewer = sub_active.widget().splitter_viewer
                    splitter_viewer.widget(1).hide()
                else:
                    QMessageBox.warning(self, '警告', "没有载入同步图像")
        except:
            QMessageBox.warning(self, '警告', "没有打开图像子窗口")

    def add_recent_path(self, file_path):
        """
            添加到最近文件中
        """
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

    def Registration_match(self):
        """
            执行图像配准功能
        """
        sub_active = self.mdiArea.activeSubWindow()
        # 如果是图像显示窗口，不是空窗口或者监控窗口
        if hasattr(sub_active.widget(), 'mainViewer'):
            slide_window = sub_active.widget()
            slide_window.hookSlideViewer()
        else:
            QMessageBox.warning(self, "警告", "请打开图像！")

    def cancel_registration_match(self):
        """
            取消图像配准功能
        """
        sub_active = self.mdiArea.activeSubWindow()
        # 如果时图像显示窗口
        if hasattr(sub_active.widget(), 'mainViewer'):
            slide_window = sub_active.widget()
            slide_window.cancelRegistration()
        else:
            QMessageBox.warning(self, "警告", "请打开图像！")

    def open_file_watcher(self):           # 链接open_file_manager_action
        """
            打开文件监控目录
        """
        if hasattr(self, 'file_watcher'):
            self.mdiArea.setActiveSubWindow(self.file_watcher.parent())
            return
        self.file_watcher = FileWatcher('')
        self.file_watcher.setWindowTitle('文件监控窗口')
        self.mdiArea.addSubWindow(self.file_watcher)
        self.file_watcher.closeSignal.connect(self.del_fileWatcher)
        self.file_watcher.openslideSignal.connect(self.openSlide)
        self.file_watcher.show()

    def change_file_watcher_dir(self):    # 链接change_file_manager_action
        """
            更改文件监控目录
        """
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

    def del_fileWatcher(self):  # 链接file_watcher.closeSignal
        """
            关闭filewatcher时将其属性删除,否则再次大概文件监控窗口会出错
        """
        del self.file_watcher

    def lock_mode(self, lock=True):
        """
            当手动进行配准时，要将模式切换到标注模式，同时不能够更换模式，将标注工具切换成移动工具
        """
        if lock:
            # 切换为移动模式
            self.tools_toggle(1)
            # 锁住模式切换
            self.action_enabel(False)
        else:
            self.action_enabel(True)

    def tools_toggle(self, mode2switch):
        """
            标注工具切换
        """
        sub_active = self.mdiArea.activeSubWindow()
        try:
            if hasattr(sub_active.widget(), 'controller') is False:
                return
            controller = sub_active.widget().controller
            mainViewer = sub_active.widget().mainViewer

            controller.change_label_tool(mode2switch)

            if mode2switch != 1:
                mainViewer.setMoveAllow(False)
            else:
                mainViewer.setMoveAllow(True)
            if mode2switch == 1:
                mainViewer.setCursor(Qt.ArrowCursor)
            elif mode2switch == 6:
                mainViewer.setCursor(Qt.PointingHandCursor)
            else:
                mainViewer.setCursor(Qt.CrossCursor)
        except:
            QMessageBox.warning(self, "警告",  "切换标注工具时出错")
            return

    def disconnect_action_signal(self, action: QAction):
        """
            断开信号与函数的连接
        """
        action.triggered.disconnect()

    def annotaionColorConnections(self):
        """
            进行链接：绑定状态栏中的颜色与标注颜色
        """
        # 解除activate_color_action与之前绑定的函数的链接
        self.disconnect_action_signal(self.activate_color_action1)
        self.disconnect_action_signal(self.activate_color_action2)
        self.disconnect_action_signal(self.activate_color_action3)
        self.disconnect_action_signal(self.activate_color_action4)
        sub_active = self.mdiArea.activeSubWindow()
        try:
            if hasattr(sub_active.widget(), 'controller'):
                controller = sub_active.widget().controller
                self.activate_color_action1.triggered.connect(lambda : controller.switch_label_category(0))
                self.activate_color_action2.triggered.connect(lambda: controller.switch_label_category(1))
                self.activate_color_action3.triggered.connect(lambda: controller.switch_label_category(2))
                self.activate_color_action4.triggered.connect(lambda: controller.switch_label_category(3))
                # 连接信号，选择标注时，同样会激活菜单栏中的颜色块
                self.set_color_action_checked(None, None, controller.annotationTypeIdx)
        except:
            QMessageBox.warning(self, '警告', "没有打开图像子窗口")

    def bindAnnotationColor(self, annotationType: dict):
        """
            改变工具栏中标注颜色的图块颜色
        """
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

    def onTriggered(self):
        """
            设置选中的模式checked, 一时间只能选择一种模式
        """
        # 获取触发信号的 QAction 对象
        action = self.sender()
        # 设置 QAction 被选中的状态
        action.setChecked(True)

    # TODO: 切换子窗口时，子窗口的标注工具应该与主窗口对应一致，或者切换后统一改变成移动模式
    def set_window_status(self):
        """
            切换图像子窗口
        """
        sub_active = self.mdiArea.activeSubWindow()
        # 如果打开的是并不是图像窗口，那么需要将菜单栏的使能关闭
        try:
            if hasattr(sub_active.widget(), 'mainViewer'):
                self.action_enabel(True)
            else:
                self.action_enabel(False)
        except:
            print("Main Window 425行")

        try:
            if hasattr(sub_active.widget(), 'mainViewer'):
                self.bindAnnotationColor(sub_active.widget().controller.annotationTypeDict)
                self.annotaionColorConnections()

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
                    if sub_window.windowTitle() == '文件监控窗口':
                        file_watcher = sub_window.window().file_watcher
                        file_watcher.stop_timer()
        except:
            print("MainWindow 453 行")

    def add_recent_file(self, path, fist=False):
        """
            将最近打开文件夹中添加路径
        """
        action = QAction(path)
        action.triggered.connect(lambda: self.openSlide(path))
        if fist:
            self.recentFileActions.insert(0, action)
        else:
            self.recentFileActions.append(action)

    def set_style(self):
        self.setStyleSheet("""* {font-family: 宋体; font-size: 14px;}""")

    def setRoiSize(self):
        from window.dialog.SizeInputDialog import SizeInputDialog
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