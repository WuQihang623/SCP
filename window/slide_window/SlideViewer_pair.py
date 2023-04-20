import openslide
from PyQt5.QtCore import Qt, pyqtSlot
from window.slide_window.utils.SlideHelper import SlideHelper
from window.slide_window.TileLoader.TileLoader import TileManager
from window.slide_window.SlideViewer import SlideViewer
from PyQt5.QtGui import QWheelEvent, QMouseEvent

class SlideviewerPair(SlideViewer):
    def __init__(self, paired=False):
        super(SlideviewerPair, self).__init__(paired)

    # 载入slide
    def load_slide(self, slide_path, zoom_step=1.35):
        super(SlideviewerPair, self).load_slide(slide_path)

    def eventFilter(self, qobj: 'QObject', event: 'QEvent') -> bool:
        return False

    # 监听所有窗口小部件的事件
    def eventFilter1(self, qobj: 'QObject', event: 'QEvent') -> bool:
        # 如果不是鼠标事件或者滚轮事件，则不进行事件的传递
        event_porcessed = False
        # 鼠标事件
        if isinstance(event, QMouseEvent):
            event_porcessed = self.processMouseEvent(event)
        elif isinstance(event, QWheelEvent):
            event_porcessed = self.processWheelEvent(event)

        return event_porcessed