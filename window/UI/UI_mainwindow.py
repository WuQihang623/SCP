# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'scp.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1085, 803)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.mdiArea = QtWidgets.QMdiArea(self.centralwidget)
        self.mdiArea.setGeometry(QtCore.QRect(0, 0, 1081, 731))
        self.mdiArea.setObjectName("mdiArea")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1085, 23))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        self.open_recent_slide_menu = QtWidgets.QMenu(self.menu)
        self.open_recent_slide_menu.setObjectName("open_recent_slide_menu")
        self.paired_slide_menu = QtWidgets.QMenu(self.menu)
        self.paired_slide_menu.setObjectName("paired_slide_menu")
        self.file_manager_menu = QtWidgets.QMenu(self.menu)
        self.file_manager_menu.setObjectName("file_manager_menu")
        self.edit_menu = QtWidgets.QMenu(self.menubar)
        self.edit_menu.setObjectName("edit_menu")
        self.tool_menu = QtWidgets.QMenu(self.menubar)
        self.tool_menu.setObjectName("tool_menu")
        self.mode_menu = QtWidgets.QMenu(self.menubar)
        self.mode_menu.setObjectName("mode_menu")
        MainWindow.setMenuBar(self.menubar)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.open_slide_action = QtWidgets.QAction(MainWindow)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("logo/load.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.open_slide_action.setIcon(icon)
        self.open_slide_action.setObjectName("open_slide_action")
        self.fill_screen_action = QtWidgets.QAction(MainWindow)
        self.fill_screen_action.setObjectName("fill_screen_action")
        self.shot_screen_action = QtWidgets.QAction(MainWindow)
        self.shot_screen_action.setObjectName("shot_screen_action")
        self.quit = QtWidgets.QAction(MainWindow)
        self.quit.setObjectName("quit")
        self.rect_resiz_action = QtWidgets.QAction(MainWindow)
        self.rect_resiz_action.setObjectName("rect_resiz_action")
        self.recall_action = QtWidgets.QAction(MainWindow)
        self.recall_action.setObjectName("recall_action")
        self.fixed_rect_action = QtWidgets.QAction(MainWindow, checkable=True)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("logo/ROI.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.fixed_rect_action.setIcon(icon1)
        self.fixed_rect_action.setObjectName("fixed_rect_action")
        self.rect_action = QtWidgets.QAction(MainWindow, checkable=True)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("logo/rect.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.rect_action.setIcon(icon2)
        self.rect_action.setObjectName("rect_action")
        self.polygon_action = QtWidgets.QAction(MainWindow, checkable=True)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("logo/line.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.polygon_action.setIcon(icon3)
        self.polygon_action.setObjectName("polygon_action")
        self.measure_tool_action = QtWidgets.QAction(MainWindow, checkable=True)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("logo/rule.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.measure_tool_action.setIcon(icon4)
        self.measure_tool_action.setObjectName("measure_tool_action")
        self.modify_action = QtWidgets.QAction(MainWindow, checkable=True)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap("logo/change.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.modify_action.setIcon(icon5)
        self.modify_action.setObjectName("modify_action")
        self.move_action = QtWidgets.QAction(MainWindow, checkable=True)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap("logo/delete.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.move_action.setIcon(icon6)
        self.move_action.setObjectName("move_action")
        self.annotation_action = QtWidgets.QAction(MainWindow, checkable=True)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap("logo/annotation.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.annotation_action.setIcon(icon7)
        self.annotation_action.setObjectName("annotation_action")
        self.diagnose_action = QtWidgets.QAction(MainWindow, checkable=True)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap("logo/diagnose.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.diagnose_action.setIcon(icon8)
        self.diagnose_action.setObjectName("diagnose_action")
        self.microenv_action = QtWidgets.QAction(MainWindow, checkable=True)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap("logo/cell_segment.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.microenv_action.setIcon(icon9)
        self.microenv_action.setObjectName("microenv_action")
        self.pdl1_action = QtWidgets.QAction(MainWindow, checkable=True)
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap("logo/IHC.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pdl1_action.setIcon(icon10)
        self.pdl1_action.setObjectName("pdl1_action")
        self.multimodal_action = QtWidgets.QAction(MainWindow, checkable=True)
        icon13 = QtGui.QIcon()
        icon13.addPixmap(QtGui.QPixmap("logo/gene.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.multimodal_action.setIcon(icon13)
        self.multimodal_action.setObjectName("multimodal_action")
        self.open_paired_action = QtWidgets.QAction(MainWindow)
        self.open_paired_action.setObjectName("open_paired_action")
        self.open_paired_win_action = QtWidgets.QAction(MainWindow)
        self.open_paired_win_action.setObjectName("open_paired_win_action")
        self.close_paired_win_action = QtWidgets.QAction(MainWindow)
        self.close_paired_win_action.setObjectName("close_paired_win_action")
        self.synchronization_action = QtWidgets.QAction(MainWindow)
        self.synchronization_action.setObjectName("synchronization_action")
        self.cancel_synchronization_action = QtWidgets.QAction(MainWindow)
        self.cancel_synchronization_action.setObjectName("cancel_synchronization_action")
        self.open_file_manager_action = QtWidgets.QAction(MainWindow)
        self.open_file_manager_action.setObjectName("open_file_manager_action")
        self.change_file_manager_action = QtWidgets.QAction(MainWindow)
        self.change_file_manager_action.setObjectName("change_file_manager_action")
        self.batch_process_action = QtWidgets.QAction(MainWindow)
        self.batch_process_action.setObjectName("batch_process")
        self.stop_batch_process_action = QtWidgets.QAction(MainWindow)
        self.stop_batch_process_action.setObjectName('stop_batch_process_action')

        pixmap = QtGui.QPixmap(20, 20)
        color = QtGui.QColor(255, 255, 255, 255)
        pixmap.fill(color)
        icon12 = QtGui.QIcon(pixmap)
        self.activate_color_action1 = QtWidgets.QAction(MainWindow, checkable=True)
        self.activate_color_action1.setIcon(icon12)
        self.activate_color_action1.setObjectName("activate_color_action1")
        self.activate_color_action2 = QtWidgets.QAction(MainWindow, checkable=True)
        self.activate_color_action2.setIcon(icon12)
        self.activate_color_action2.setObjectName("activate_color_action2")
        self.activate_color_action3 = QtWidgets.QAction(MainWindow, checkable=True)
        self.activate_color_action3.setIcon(icon12)
        self.activate_color_action3.setObjectName("activate_color_action3")
        self.activate_color_action4 = QtWidgets.QAction(MainWindow, checkable=True)
        self.activate_color_action4.setIcon(icon12)
        self.activate_color_action4.setObjectName("activate_color_action4")


        self.convert_color_space_action = QtWidgets.QAction(MainWindow)
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap("logo/color.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.convert_color_space_action.setIcon(icon11)
        self.convert_color_space_action.setObjectName("convert_color_space_action")
        self.paired_slide_menu.addAction(self.open_paired_action)
        self.paired_slide_menu.addAction(self.open_paired_win_action)
        self.paired_slide_menu.addAction(self.close_paired_win_action)
        self.paired_slide_menu.addAction(self.synchronization_action)
        self.paired_slide_menu.addAction(self.cancel_synchronization_action)
        self.file_manager_menu.addAction(self.open_file_manager_action)
        self.file_manager_menu.addAction(self.change_file_manager_action)
        self.file_manager_menu.addAction(self.batch_process_action)
        self.file_manager_menu.addAction(self.stop_batch_process_action)
        self.menu.addAction(self.open_slide_action)
        self.menu.addAction(self.open_recent_slide_menu.menuAction())
        self.menu.addAction(self.paired_slide_menu.menuAction())
        self.menu.addAction(self.file_manager_menu.menuAction())
        self.menu.addSeparator()
        self.menu.addAction(self.quit)
        self.edit_menu.addAction(self.rect_resiz_action)
        self.edit_menu.addAction(self.convert_color_space_action)
        self.tool_menu.addAction(self.fixed_rect_action)
        self.tool_menu.addAction(self.rect_action)
        self.tool_menu.addAction(self.polygon_action)
        self.tool_menu.addAction(self.measure_tool_action)
        self.tool_menu.addAction(self.modify_action)
        self.tool_menu.addAction(self.move_action)
        self.mode_menu.addAction(self.annotation_action)
        self.mode_menu.addAction(self.diagnose_action)
        self.mode_menu.addAction(self.microenv_action)
        self.mode_menu.addAction(self.pdl1_action)
        self.mode_menu.addAction(self.multimodal_action)
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.edit_menu.menuAction())
        self.menubar.addAction(self.tool_menu.menuAction())
        self.menubar.addAction(self.mode_menu.menuAction())
        self.toolBar.addAction(self.open_slide_action)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.annotation_action)
        self.toolBar.addAction(self.diagnose_action)
        self.toolBar.addAction(self.microenv_action)
        self.toolBar.addAction(self.pdl1_action)
        self.toolBar.addAction(self.multimodal_action)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.move_action)
        self.toolBar.addAction(self.modify_action)
        self.toolBar.addAction(self.fixed_rect_action)
        self.toolBar.addAction(self.rect_action)
        self.toolBar.addAction(self.polygon_action)
        self.toolBar.addAction(self.measure_tool_action)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.activate_color_action1)
        self.toolBar.addAction(self.activate_color_action2)
        self.toolBar.addAction(self.activate_color_action3)
        self.toolBar.addAction(self.activate_color_action4)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.convert_color_space_action)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menu.setTitle(_translate("MainWindow", "开始"))
        self.paired_slide_menu.setTitle(_translate("MainWindow", "同步图像"))
        self.file_manager_menu.setTitle(_translate("MainWindow", "文件管理"))
        self.edit_menu.setTitle(_translate("MainWindow", "编辑"))
        self.tool_menu.setTitle(_translate("MainWindow", "工具"))
        self.mode_menu.setTitle(_translate("MainWindow", "模式选择"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.open_slide_action.setText(_translate("MainWindow", "导入文件"))
        self.fill_screen_action.setText(_translate("MainWindow", "切换全屏显示(Q)"))
        self.shot_screen_action.setText(_translate("MainWindow", "截图"))
        self.quit.setText(_translate("MainWindow", "退出"))
        self.rect_resiz_action.setText(_translate("MainWindow", "矩形尺寸设置"))
        self.recall_action.setText(_translate("MainWindow", "撤回"))
        self.fixed_rect_action.setText(_translate("MainWindow", "固定矩形"))
        self.rect_action.setText(_translate("MainWindow", "矩形"))
        self.polygon_action.setText(_translate("MainWindow", "多边形"))
        self.measure_tool_action.setText(_translate("MainWindow", "测量工具"))
        self.modify_action.setText(_translate("MainWindow", "修改工具"))
        self.move_action.setText(_translate("MainWindow", "移动"))
        self.annotation_action.setText(_translate("MainWindow", "图像标注"))
        self.diagnose_action.setText(_translate("MainWindow", "全切片辅助诊断"))
        self.microenv_action.setText(_translate("MainWindow", "肿瘤微环境分析"))
        self.pdl1_action.setText(_translate("MainWindow", "PD-L1评分"))
        self.multimodal_action.setText(_translate("MainWindow", "多模态"))
        self.open_paired_action.setText(_translate("MainWindow", "导入同步图像"))
        self.open_paired_win_action.setText(_translate("MainWindow", "显示同步图像"))
        self.close_paired_win_action.setText(_translate("MainWindow", "关闭同步图像"))
        self.synchronization_action.setText(_translate("MainWindow", "同步"))
        self.cancel_synchronization_action.setText(_translate("MainWindow", "取消同步"))
        self.open_file_manager_action.setText(_translate("MainWindow", "打开文件管理"))
        self.change_file_manager_action.setText(_translate("MainWindow", "更改管理文件夹"))
        self.batch_process_action.setText(_translate("MainWindow", "批处理"))
        self.stop_batch_process_action.setText(_translate("MainWindow", "停止批处理"))
        self.open_recent_slide_menu.setTitle(_translate("MainWindow", "打开最近文件"))
        self.convert_color_space_action.setText(_translate("MainWindow", "颜色空间转换"))
        self.activate_color_action1.setText(_translate("MainWindow", "颜色1"))
        self.activate_color_action2.setText(_translate("MainWindow", "颜色2"))
        self.activate_color_action3.setText(_translate("MainWindow", "颜色3"))
        self.activate_color_action4.setText(_translate("MainWindow", "颜色4"))

    # 只有在载入图像的叶片中激活这些功能
    def action_enabel(self, enable=True):
        self.open_paired_action.setEnabled(enable)
        self.open_paired_win_action.setEnabled(enable)
        self.close_paired_win_action.setEnabled(enable)
        self.fixed_rect_action.setEnabled(enable)
        self.rect_action.setEnabled(enable)
        self.polygon_action.setEnabled(enable)
        self.measure_tool_action.setEnabled(enable)
        self.modify_action.setEnabled(enable)
        self.move_action.setEnabled(enable)
        self.activate_color_action1.setEnabled(enable)
        self.activate_color_action2.setEnabled(enable)
        self.activate_color_action3.setEnabled(enable)
        self.activate_color_action4.setEnabled(enable)
        self.convert_color_space_action.setEnabled(enable)
        self.fill_screen_action.setEnabled(enable)
        self.synchronization_action.setEnabled(enable)
        self.cancel_synchronization_action.setEnabled(enable)

    # 只有在标注模式下这些action的使能才会被打开
    def annotation_action_enable(self, enable):
        self.fixed_rect_action.setEnabled(enable)
        self.rect_action.setEnabled(enable)
        self.polygon_action.setEnabled(enable)
        self.measure_tool_action.setEnabled(enable)
        self.modify_action.setEnabled(enable)
        self.move_action.setEnabled(enable)
        self.activate_color_action1.setEnabled(enable)
        self.activate_color_action2.setEnabled(enable)
        self.activate_color_action3.setEnabled(enable)
        self.activate_color_action4.setEnabled(enable)

    # 当选择标注颜色后，会使得菜单栏的颜色块被激活
    def set_color_action_checked(self, idx):
        # 阻止信号发送
        self.activate_color_action1.blockSignals(True)
        self.activate_color_action2.blockSignals(True)
        self.activate_color_action3.blockSignals(True)
        self.activate_color_action4.blockSignals(True)

        self.activate_color_action1.setChecked(False)
        self.activate_color_action2.setChecked(False)
        self.activate_color_action3.setChecked(False)
        self.activate_color_action4.setChecked(False)
        if idx == 0:
            self.activate_color_action1.setChecked(True)
        elif idx == 1:
            self.activate_color_action2.setChecked(True)
        elif idx == 2:
            self.activate_color_action3.setChecked(True)
        elif idx == 3:
            self.activate_color_action4.setChecked(True)

        # 打开信号发送通道
        self.activate_color_action1.blockSignals(False)
        self.activate_color_action2.blockSignals(False)
        self.activate_color_action3.blockSignals(False)
        self.activate_color_action4.blockSignals(False)