from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QPolygonF, QBrush, QColor, QPen
from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsEllipseItem, QGraphicsPolygonItem, QGraphicsLineItem

class ContourPathItem(QGraphicsPathItem):
    """
        区域与细胞轮廓的图元
    """
    def __init__(self, category, level, is_region=True):
        """
        :param category: 类型的标志（肿瘤区域，基质区域； 表皮细胞，淋巴细胞）
        :param level: 当前的level
        :param is_region: 是否为组织轮廓item,不是的话，则为细胞核item
        """
        super(ContourPathItem, self).__init__()
        self.category = category
        self.level = level
        self.is_region = is_region

class EllipseItem(QGraphicsEllipseItem):
    """
        细胞核点的图元
    """
    def __init__(self, x, y, w, h, category, level, is_region=False):
        super(EllipseItem, self).__init__(x, y, w, h)
        self.category = category
        self.level = level
        self.is_region = is_region

class TriangleItem(QGraphicsPolygonItem):
    """
        对比的细胞核三角形图元
    """
    def __init__(self, x, y, color, category, level, width=5, is_region=False):
        super().__init__(None)
        self.category = category
        self.level = level
        self.is_region = is_region

        triangle = QPolygonF([
            QPointF(0, -width),
            QPointF(width, width),
            QPointF(-width, width)
        ])
        self.setPolygon(triangle)
        brush = QBrush(QColor(*color))
        self.setBrush(brush)
        self.setPos(x, y)

class CircleItem(QGraphicsEllipseItem):
    """
        对比的细胞核圆形图元
    """
    def __init__(self, x, y, color, category, level, radius=20, is_region=False):
        super().__init__(x-radius, y-radius, 2 * radius, 2 * radius)
        self.category = category
        self.level = level
        self.is_region = is_region
        # 设置圆形的边框颜色
        pen = QPen(QColor(*color))
        # 设置圆形的边框
        self.setPen(pen)

class LineItem(QGraphicsLineItem):
    """
        细胞核分割切patch的线条图元
    """
    def __init__(self, x1, y1, x2, y2, color, level, is_region=False, category="Line"):
        super().__init__(x1, y1, x2, y2)
        pen = QPen(QColor(*color))
        pen.setStyle(Qt.DashLine)
        pen.setWidth(1)
        self.setPen(pen)
        self.category = category
        self.level = level
        self.is_region = is_region
        self.setZValue(35)

    def setColor(self, color):
        self.setColor(QColor(*color))