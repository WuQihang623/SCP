from PyQt5.QtCore import QSize, QRectF, Qt, QSizeF, QPointF, QRect, QPoint
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsItemGroup, QGraphicsView


def paint_screenshot_image(painter: QPainter, scene: QGraphicsScene, image_size: QSize, scene_rect: QRectF = QRectF(),
                           transparent_background=False) -> QImage:
    painter.fillRect(QRect(QPoint(0, 0), image_size), painter.background().color())
    rendered_size = scene_rect.size().scaled(QSizeF(image_size), Qt.KeepAspectRatio)
    dsize = QSizeF(image_size) - rendered_size
    top_left = QPointF(dsize.width() / 2, dsize.height() / 2)
    scene.render(painter, QRectF(top_left, rendered_size), scene_rect, Qt.KeepAspectRatio)


def build_screenshot_image(scene: QGraphicsScene, image_size: QSize, scene_rect: QRectF = QRectF()) -> QImage:
    image = QImage(image_size, QImage.Format_RGBA8888)
    painter = QPainter(image)
    paint_screenshot_image(painter, scene, image_size, scene_rect)
    painter.end()
    return image


