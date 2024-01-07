from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QPolygonF, QBrush, QColor
from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsEllipseItem, QGraphicsPolygonItem


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