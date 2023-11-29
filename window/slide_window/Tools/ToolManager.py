"""
实现工具的调度，绘制标注，以及将标注的结果传给Anootation
"""
import math
import os
import json
import numpy as np
from collections import OrderedDict

from PyQt5.QtCore import Qt, pyqtSignal, QPointF, QObject
from PyQt5.QtGui import QPainterPath, QColor
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsEllipseItem

from window.slide_window.Tools import DrawFixedRect, DrawRect, DrawPolygon, MeasureTool, DrawPoint
from function.delDictItem import delDictItem

class ToolManager(QObject):
    # 当标注被选择时用红色显示
    CHOOSED_COLOR= Qt.red
    sendAnnotationSignal = pyqtSignal(dict, int)
    # 发送被选中的item的bbox，用于跳转到该位置
    switch2choosedItemSignal = pyqtSignal(list, int)
    # 删除所有标注时，将整个画面清除的信号
    clearViewSignal = pyqtSignal(bool)
    sendModifiedAnnotationSignal = pyqtSignal(dict, int)
    def __init__(self, view: QGraphicsView, scene: QGraphicsScene):
        super(ToolManager, self).__init__()
        self.view = view
        self.scene = scene
        # 标注工具的标志
        self.TOOL_FLAG = 1
        # 手动配准时双击能够设定位置的标志
        self.registration_flag = False
        # 设置移动控制点的标志
        self.modifyAnnotationFlag = False
        """
        1: 移动工具
        2： 固定矩形工具
        3： 矩形工具
        4： 多边形工具
        5： 测量工具
        6： 修改工具
        """
        # 所有的标注信息存储
        self.Annotations = OrderedDict()
        # 初始化标注工具
        self.draw_fixedRect = DrawFixedRect(self.scene, self.view)
        self.draw_Rect = DrawRect(self.scene, self.view)
        self.draw_polygon = DrawPolygon(self.scene, self.view)
        self.measure_tool = MeasureTool(self.scene, self.view)
        self.draw_point = DrawPoint(self.scene, self.view)
        # 当闭合多边形时，发送信号，将标注添加到self.Annotation与annotation中
        self.draw_polygon.PolygonClosureSignal.connect(self.addAnnotation)

        # 当前被选中的标注
        self.choosed_idx = None

    # 设置不同的标注工具
    def set_annotation_mode(self, mode):
        if self.TOOL_FLAG != mode:
            # 设置模式
            self.TOOL_FLAG = mode
            # 将当前没画完的结果擦除
            self.draw_fixedRect.stopDraw()
            self.draw_Rect.stopDraw()
            self.draw_polygon.stopDraw()
            self.measure_tool.stopDraw()

    # 当手动进行配准时切换标志位
    def set_registration_flag(self, flag: bool):
        print("设置标志位",flag)
        self.registration_flag = flag
        if flag is False:
            self.draw_point.deleteItem()
        else:
            self.draw_point.restart()

    # 取消当前标注时，将当前的绘制过程取消
    def cancel_drawing(self):
        self.draw_fixedRect.stopDraw()
        self.draw_Rect.stopDraw()
        self.draw_polygon.stopDraw()
        self.measure_tool.stopDraw()

    # 鼠标点击动作，进行标注的绘制
    def mousePressEvent(self, event, downsample):
        # 固定矩形工具
        if self.TOOL_FLAG == 2:
            self.draw_fixedRect.mousePressEvent(event, downsample)
        elif self.TOOL_FLAG == 3:
            self.draw_Rect.mousePressEvent(event, downsample)
        elif self.TOOL_FLAG == 4:
            self.draw_polygon.mousePressEvent(event, downsample)
        elif self.TOOL_FLAG == 5:
            self.measure_tool.mousePressEvent(event, downsample)
        elif self.TOOL_FLAG == 6:
            """
            如果点击到的标注已经被激活，则不用理会
            如果点到的是已激活的控制点，则
            如果点到的标注没有被激活，则将其激活
            """
            item = self.view.itemAt(event.pos())
            # 如果不是控制点
            if not isinstance(item, QGraphicsEllipseItem):
                # 查看这个item的索引
                item_idx = self.getAnnotationItemIdx(item)
                if item_idx is not None:
                    # 如果点击的item_idx不是当前被选中的item，则将当前item激活
                    if item_idx != self.choosed_idx:
                        # 如果当前有激活的标注，则取消激活
                        self.reactivateItem(item_idx, downsample)
            # 如果是控制点，则要查看是哪一个标注的,哪个点，并设置标志，可以进行标注的更改
            else:
                # 获取当前控制点的索引信息
                self.control_point_idx = self.getControlItemIdx(item)
                self.control_point_item = item
                # 设置标志，能够移动控制点
                self.modifyAnnotationFlag = True

    # 鼠标移动
    def mouseMoveEvent(self, event, downsample):
        # 固定矩形工具
        if self.TOOL_FLAG == 2:
            self.draw_fixedRect.mouseMoveEvent(event, downsample)
        elif self.TOOL_FLAG == 3:
            self.draw_Rect.mouseMoveEvent(event, downsample)
        elif self.TOOL_FLAG == 4:
            self.draw_polygon.mouseMoveEvent(event, downsample)
        elif self.TOOL_FLAG == 5:
            self.measure_tool.mouseMoveEvent(event, downsample)
        elif self.TOOL_FLAG == 6:
            if self.modifyAnnotationFlag and self.choosed_idx is not None \
                    and self.control_point_idx is not None:
                scene_pos = self.view.mapToScene(event.pos())
                annotation = self.Annotations[f"标注{self.choosed_idx}"]
                # 如果是固定矩形
                if annotation['tool'] == '固定矩形':
                    points = annotation['location']
                    w = points[1][0] - points[0][0]
                    h = points[1][1] - points[0][1]
                    annotation['annotation_item'].setRect(scene_pos.x(), scene_pos.y(), w / downsample, h / downsample)
                    annotation['location'][0] = [scene_pos.x() * downsample, scene_pos.y() * downsample]
                    annotation['location'][1] = [scene_pos.x() * downsample + w, scene_pos.y() * downsample + h]
                elif annotation['tool'] == '矩形':
                    annotation['location'][self.control_point_idx] = [scene_pos.x() * downsample, scene_pos.y() * downsample]
                    points = annotation['location']
                    annotation['annotation_item'].setRect(min(points[0][0], points[1][0]) / downsample,
                                                          min(points[0][1], points[1][1]) / downsample,
                                                          abs(points[0][0] - points[1][0]) / downsample,
                                                          abs(points[0][1] - points[1][1]) / downsample)
                elif annotation['tool'] == '测量工具':
                    annotation['location'][self.control_point_idx] = [scene_pos.x() * downsample, scene_pos.y() * downsample]
                    points = annotation['location']
                    annotation['annotation_item'].setLine(points[0][0] / downsample,
                                                          points[0][1] / downsample,
                                                          points[1][0] / downsample,
                                                          points[1][1] / downsample)
                    distance = math.sqrt((points[0][0] - points[1][0]) ** 2 +
                                         (points[0][1] - points[1][1]) ** 2) * self.measure_tool.mpp
                    annotation['text_item'].setPlainText(f"{distance:.2f}μm")
                    annotation['text_item'].setPos((points[0][0] + points[1][0]) / 2 / downsample,
                                                   (points[0][1] + points[1][1]) / 2 / downsample)
                elif annotation['tool'] == '多边形':
                    annotation['location'][self.control_point_idx] = [scene_pos.x() * downsample,
                                                                      scene_pos.y() * downsample]
                    points = annotation['location']
                    path = QPainterPath()
                    for idx, point in enumerate(points):
                        x = point[0] / downsample
                        y = point[1] / downsample
                        point = QPointF(x, y)
                        if idx == 0:
                            path.moveTo(point)
                        else:
                            path.lineTo(point)
                    path.closeSubpath()
                    annotation['annotation_item'].setPath(path)
                else:
                    return
                self.control_point_item.setPos(scene_pos.x() - 4, scene_pos.y() - 4)
    # 鼠标释放
    def mouseReleaseEvent(self, event, downsample):
        # 固定矩形工具
        annotaion_info = None
        if self.TOOL_FLAG == 2:
            annotaion_info = self.draw_fixedRect.mouseReleaseEvent(event, downsample)
        elif self.TOOL_FLAG == 3:
            annotaion_info = self.draw_Rect.mouseRelease(event, downsample)
        elif self.TOOL_FLAG == 4:
            annotaion_info = self.draw_polygon.mouseReleaseEvent(event, downsample)
        elif self.TOOL_FLAG == 5:
            annotaion_info = self.measure_tool.mouseReleaseEvent(event, downsample)
        elif self.TOOL_FLAG == 6:
            annotation = self.Annotations[f"标注{self.choosed_idx}"]
            annotation2tree = annotation.copy()
            annotation2tree.pop("annotation_item", None)
            annotation2tree.pop('text_item', None)
            annotation2tree.pop("control_point_items", None)
            self.sendModifiedAnnotationSignal.emit(annotation2tree, self.choosed_idx)
            self.modifyAnnotationFlag = False
            self.control_point_idx = None

        # TODO：添加标注到self.Annotations中
        if annotaion_info is not None:
            self.addAnnotation(annotaion_info, downsample)
        return annotaion_info

    def mouseDoubleClickEvent(self, event, downsample):
        if self.registration_flag and self.TOOL_FLAG==1:
            self.draw_point.mouseDoubleClickEvent(event, downsample)

    # 当scene改变后，需要重新绘制当前绘制的这个形状
    def redraw(self, level, downsample):
        width = int(4 / self.view.transform().m11())
        # 重新绘制当前绘制的标注
        if self.TOOL_FLAG == 2:
            self.draw_fixedRect.redraw(downsample, width)
        elif self.TOOL_FLAG == 3:
            self.draw_Rect.redraw(downsample, width)
        elif self.TOOL_FLAG == 4:
            self.draw_polygon.redraw(downsample, width)
        elif self.TOOL_FLAG == 5:
            self.measure_tool.redraw(downsample, width)
        if self.registration_flag:
            self.draw_point.redraw(downsample)

        # 重新绘制绘制好的标注
        for idx, (name, annotation) in enumerate(self.Annotations.items()):
            annotation_item, control_point_items, text_item = \
                self.drawAnnotaion(annotation, downsample, choosed=idx==self.choosed_idx)

            self.Annotations[name]['annotation_item'] = annotation_item
            self.Annotations[name]['control_point_items'] = control_point_items
            if text_item is not None:
                self.Annotations[name]['text_item'] = text_item


    # 设置标注工具的类型和颜色
    def set_annotationColor(self, type, color):
        self.draw_fixedRect.set_AnnotationColor(type, color)
        self.draw_Rect.set_AnnotationColor(type, color)
        self.draw_polygon.set_AnnotationColor(type, color)
        self.measure_tool.set_AnnotationColor(type, color)

    # 绘制标注完成，添加到ToolManager与annotation中
    def addAnnotation(self, annotation, downsample):
        if annotation is not None:
            num_annotation = len(self.Annotations)
            self.Annotations[f"标注{num_annotation}"] = annotation

            annotation2tree = annotation.copy()
            annotation2tree.pop("annotation_item", None)
            annotation2tree.pop('text_item', None)
            annotation2tree.pop("control_point_items", None)
            self.sendAnnotationSignal.emit(annotation2tree, num_annotation)

            # TODO：把上一个选中的标注item删除，重新绘制，并将当前Annotation设置为被选中的状态
            if self.choosed_idx is not None:
                self.remove_AnnotationItem(self.choosed_idx)
                annotation_item, control_point_items, text_item = \
                    self.drawAnnotaion(self.Annotations[f"标注{self.choosed_idx}"], downsample)
                # 修改self.Annotations
                self.updateAnnotationDict(f"标注{self.choosed_idx}", annotation_item, control_point_items, text_item)

                self.remove_AnnotationItem(num_annotation)
                annotation_item, control_points_item, text_item = \
                    self.drawAnnotaion(self.Annotations[f"标注{num_annotation}"], downsample, True)
                self.updateAnnotationDict(f"标注{num_annotation}", annotation_item, control_points_item, text_item)
            else:
                self.remove_AnnotationItem(num_annotation)
                annotation_item, control_point_items, text_item = \
                    self.drawAnnotaion(self.Annotations[f"标注{num_annotation}"], downsample, True)
                self.updateAnnotationDict(f"标注{num_annotation}", annotation_item, control_point_items, text_item)
            self.choosed_idx = len(self.Annotations) - 1

    # 更新annotation_item， control_points_items， text_item
    def updateAnnotationDict(self, annotation_name, annotation_item, control_point_items, text_item):
        self.Annotations[annotation_name]['annotation_item'] = annotation_item
        self.Annotations[annotation_name]['control_point_items'] = control_point_items
        if text_item is not None:
            self.Annotations[annotation_name]['text_item'] = text_item

    """
    当更换选中标注的时候，需要重新绘制被替代的和替代的，并且要更新self.Annotations
    当视图缩放时也要重新绘制，并且要更新self.Annotations
    """
    def drawAnnotaion(self, annotation, downsample, choosed=False):
        """
        :param downsample: 当前scene的下采样倍数
        :param choosed_index: 当前选中的标注索引
        :return:
        """
        width = 4
        text_size = 15

        # 设置绘制标注的颜色
        color = QColor(*annotation['color']) if choosed is False else self.CHOOSED_COLOR
        if annotation['tool'] == '固定矩形':
            annotation_item, control_point_items, text_item = \
                self.draw_fixedRect.draw(points=annotation['location'],
                                     color=color,
                                     width = width,
                                     downsample=downsample,
                                     choosed=choosed)
        elif annotation['tool'] == '矩形':
            annotation_item, control_point_items, text_item = \
                self.draw_Rect.draw(points=annotation['location'],
                                color=color,
                                width=width,
                                downsample=downsample,
                                choosed=choosed)
        elif annotation['tool'] == '多边形':
            annotation_item, control_point_items, text_item = \
                self.draw_polygon.draw(points=annotation['location'],
                                   color=color,
                                   width=width,
                                   downsample=downsample,
                                   choosed=choosed)
        # 测量工具
        else:
            annotation_item, control_point_items, text_item = \
                self.measure_tool.draw(points=annotation['location'],
                                   distance=annotation['distance'],
                                   width=width,
                                   text_width=text_size,
                                   color=color,
                                   downsample=downsample,
                                   choosed=choosed)

        return annotation_item, control_point_items, text_item

    """
    删除item，配合选中标注，删除标注的功能
    """
    def remove_AnnotationItem(self, idx):
        if self.Annotations.get(f"标注{idx}"):
            annotation = self.Annotations[f'标注{idx}']
            # 删除
            self.scene.removeItem(annotation['annotation_item'])
            for item in annotation['control_point_items']:
                self.scene.removeItem(item)
            if annotation.get('text_item') is not None:
                self.scene.removeItem(annotation.get('text_item'))

    # TODO: 跳转到当前标注的视图下
    def switch2choosedItem(self, idx):
        # 计算选中的标注所在的区域，将该标注设置到当前视图的中心位置
        if self.Annotations.get(f'标注{idx}') is not None:
            annotation = self.Annotations[f'标注{idx}']
            location = np.array(annotation['location'])
            x1 = location[:, 0].min()
            x2 = location[:, 0].max()
            y1 = location[:, 1].min()
            y2 = location[:, 1].max()

            self.switch2choosedItemSignal.emit([x1, y1, x2, y2], idx)

    # 删除上一个激活的item并重画，再重画当前激活的item
    def reactivateItem(self, choosed_idx, downsample):
        if self.choosed_idx is not None:
            self.remove_AnnotationItem(self.choosed_idx)
            annotation_item, control_point_items, text_item = \
                self.drawAnnotaion(self.Annotations[f"标注{self.choosed_idx}"], downsample)
            # 修改self.Annotations
            self.updateAnnotationDict(f"标注{self.choosed_idx}", annotation_item, control_point_items, text_item)
        self.choosed_idx = choosed_idx
        self.remove_AnnotationItem(self.choosed_idx)
        annotation_item, control_point_items, text_item = \
            self.drawAnnotaion(self.Annotations[f"标注{self.choosed_idx}"], downsample, True)
        # 修改self.Annotations
        self.updateAnnotationDict(f"标注{self.choosed_idx}", annotation_item, control_point_items, text_item)

    # 修改self.Annotation,响应修改标注的action
    def changeAnnotation(self, idx, new_type, new_color):
        self.Annotations[f"标注{idx}"]['type'] = new_type
        self.Annotations[f"标注{idx}"]['color'] = new_color

    # 输入为要删除的标注的索引，将图元删除
    def deleteAnnotation(self, idx):
        # 先将图元删除
        self.remove_AnnotationItem(idx)
        self.Annotations = delDictItem(self.Annotations, idx)
        self.choosed_idx = None

    # 清除所有的标注
    def clearAnnotations(self):
        self.Annotations = OrderedDict()
        # 发送清除画面的信号
        self.clearViewSignal.emit(True)
        self.choosed_idx = None

    # 同步Annotation中的信息
    def syncAnnotation(self, annotation, idx, choosed_idx):
        self.choosed_idx = choosed_idx if choosed_idx != -1 else None
        self.Annotations[f'标注{idx}'] = annotation

    # 获取item的索引
    def getAnnotationItemIdx(self, current_item):
        for idx, (name, annotation) in enumerate(self.Annotations.items()):
            if current_item == annotation['annotation_item']:
                return idx
        return None

    # 获取控制点的索引
    def getControlItemIdx(self, current_item):
        for idx, item in enumerate(self.Annotations[f'标注{self.choosed_idx}']['control_point_items']):
            if current_item == item:
                return idx
        return None