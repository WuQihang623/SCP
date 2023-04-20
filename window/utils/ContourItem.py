from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsEllipseItem


class ContourPathItem(QGraphicsPathItem):
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
    def __init__(self, x, y, w, h, category, level, is_region=False):
        super(EllipseItem, self).__init__(x, y, w, h)
        self.category = category
        self.level = level
        self.is_region = is_region