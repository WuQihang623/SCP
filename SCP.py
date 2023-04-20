import os
import qdarkstyle
from qdarkstyle.light.palette import LightPalette
import warnings

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QGraphicsScene, QGraphicsView
from window.MainWindow import MainWindow

def toggle_theme(theme):
    if theme == 'DarkStyle':
        app.setStyleSheet(qdarkstyle.load_stylesheet())
    if theme == 'LightStyle':
        app.setStyleSheet(qdarkstyle.load_stylesheet(palette=LightPalette()))

if __name__ == "__main__":
    warnings.filterwarnings('ignore')
    # 解决不同电脑不同缩放比例问题
    QGuiApplication.setAttribute(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication([])
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    # apply_stylesheet(app, theme='dark_cyan.xml')
    app.setStyle('Fusion')
    # app.setStyleSheet(qdarkstyle.load_stylesheet(palette=LightPalette()))
    window = MainWindow()
    window.show()
    app.exec_()