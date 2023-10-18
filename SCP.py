import qdarkstyle
from qdarkstyle.light.palette import LightPalette
import warnings

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication, QFont
from PyQt5.QtWidgets import QApplication
from window.MainWindow import MainWindow

def toggle_theme(theme):
    if theme == 'DarkStyle':
        app.setStyleSheet(qdarkstyle.load_stylesheet())
    if theme == 'LightStyle':
        app.setStyleSheet(qdarkstyle.load_stylesheet(palette=LightPalette()))

if __name__ == "__main__":
    warnings.filterwarnings('ignore')
    # 解决不同电脑不同缩放比例问题
    QtCore.QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    # QGuiApplication.setAttribute(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication([])
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    app.exec_()