import os
import re
import sys
import constants
from enum import Enum
from PyQt5.QtWidgets import *
from function import *
from PyQt5.QtGui import QColor, QPixmap, QIcon
from PyQt5.QtCore import pyqtSignal
from window.slide_window.utils.ColorChooseDialog import ColorChooseDialog
from window.slide_window.utils.ChangeTypeDialog import ChangeTypeDialog
from window.slide_window.utils.ChangeAnnotationDialog import ChangeAnnotationDiaglog
from window.slide_window.utils.AffirmDialog import AffirmDialog
from window.UI.UI_annotation import UI_Annotation
from function.delDictItem import delDictItem

class AnnotationMode(Enum):
    MOVE = 1
    FIXED_RECT = 2
    RECT = 3
    POLYGON = 4
    MEASURE_TOOL = 5
    MODIFY = 6

class AnnotationWidget(UI_Annotation):
    # 标注工具的模式切换信号
    toolChangeSignal = pyqtSignal(int)
    # 标注工具的颜色（标注类别）设置信号
    annotationTypeChooseSignal = pyqtSignal(str, list)
    annotationActionCheckSignal = pyqtSignal(int)

    # 更改标注类型的信号（标注类型的添加，修改，删除）
    AnnotationTypeChangeSignal = pyqtSignal(dict)
    # 点击左侧的标注栏，将当前标注选中
    updateChoosedItemSignal = pyqtSignal(int)
    # 更改标注的类别
    changeAnnotaionSignal = pyqtSignal(int, str, list)
    # 删除标注
    deleteAnnotationSignal = pyqtSignal(int)
    # 清除ToolManager中关于标注的变量,当载入标注时画面中存在标注
    clearAnnotationSignal = pyqtSignal(bool)
    # 将导入的标注信息传递给ToolManager
    syncAnnotationSignal = pyqtSignal(dict, int, int)
    # 将导入的标注显示出来
    showAnnotationSignal = pyqtSignal(bool)
    # 导入细胞核分割结果，传输路径
    loadNucleiAnnSignal = pyqtSignal(str)
    # 保存修改的细胞核pkl结果
    saveNucleiAnnSignal = pyqtSignal(str)
    AnnotationTypesPath = os.path.join(constants.cache_path, "AnnotationTypes.json")
    def __init__(self):
        super(AnnotationWidget, self).__init__()
        # 初始化
        self.AnnotationTypes = {}
        self.Annotations = OrderedDict()
        # 设置被选中的item
        self.choosed_idx = None
        # 初始化导入文件的路径
        self.annotation_file_dir = self.set_annotation_file_dir()

        # 标注工具的模式切换标志
        self.mode = AnnotationMode.MOVE
        if os.path.exists(self.AnnotationTypesPath):
            with open(self.AnnotationTypesPath, 'r') as f:
                self.AnnotationTypes = json.load(f)
                f.close()
        # 如果不存在这个路径，那么初始化一个
        else:
            self.AnnotationTypes = {"肿瘤区域": [255, 0, 0, 255],
                                    "基质区域": [0, 0, 255, 255],
                                    "其他区域": [142, 255, 111, 255]}
        self.init_AnnotationTypeTree()
        # 设置标注工具
        self.annotation_type = None
        self.annotation_color = None
        # 连接信号与槽
        self.connectBtnFunc()
        # 设置标注颜色的索引
        self.annotation_flag = -1

    def connectBtnFunc(self):
        self.addType_btn.clicked.connect(self.addCategoryAnnotaion)
        self.deleteType_btn.clicked.connect(self.delete_annotationTypeItem)

        # 当点击标注时，进行标注的激活
        self.annotationTree.itemClicked.connect(self.onClickedAnnotationTree)
        # 选择标注的类型
        self.annotationTypeTree.itemClicked.connect(self.onClickedTreeItemRow)
        # 双击标注时，进行标注描述的修改
        self.annotationTree.itemDoubleClicked.connect(self.set_description)
        # 双击标注类别时，对类别进行修改
        self.annotationTypeTree.itemDoubleClicked.connect(self.changeAnnotationTypeEvent)

        # 修改标注
        self.modify_annotation_action.triggered.connect(self.changeAnnotation)
        # 删除标注
        self.delete_annotation_action.triggered.connect(self.deleteAnnotation)

        # 导入标注
        self.loadAnnotation_btn.clicked.connect(self.loadAnnotation)
        # 保存标注
        self.save_btn.clicked.connect(self.saveAnnotations)
        # 删除所有标注
        self.clearAnnotation_btn.clicked.connect(self.clearAnnotations)
        # 导入细胞核标注
        self.loadNucleiAnn_btn.clicked.connect(self.load_nuclei)
        # 修改标注名称
        self.change_type_name_action.triggered.connect(self.changeCategory)
        self.change_type_color_action.triggered.connect(self.changeAnnotationColor)

    def init_AnnotationTypeTree(self):
        for key, rgb in self.AnnotationTypes.items():
            item = QTreeWidgetItem(self.annotationTypeTree)
            pixmap = QPixmap(20, 20)
            color = QColor(*rgb)
            pixmap.fill(color)
            item.setText(0, key)
            item.setIcon(1, QIcon(pixmap))

            # 自适应调整宽度
            self.annotationTypeTree.resizeColumnToContents(0)
            self.annotationTypeTree.resizeColumnToContents(1)

    def saveAnnotationTypeTree(self):
        self.set_activate_color_action()
        with open(self.AnnotationTypesPath, 'w') as f:
            f.write(json.dumps(self.AnnotationTypes, indent=2))
            f.close()
        return

    # 增加标注的类别，链接增加类别按钮
    def addCategoryAnnotaion(self):
        colorChooseDiaglog = ColorChooseDialog()
        if colorChooseDiaglog.exec_() == QDialog.Accepted:
            text = colorChooseDiaglog.get_text()
            color = colorChooseDiaglog.get_color()
            if text and isinstance(color, QColor):
                # 该颜色或者文本没有被添加到树中
                if text not in self.AnnotationTypes.keys() and list(color.getRgb()) not in self.AnnotationTypes.values():
                    item = QTreeWidgetItem(self.annotationTypeTree)
                    pixmap = QPixmap(20, 20)
                    pixmap.fill(color)
                    item.setText(0, text)
                    item.setIcon(1, QIcon(pixmap))
                    self.AnnotationTypes[text] = list(color.getRgb())
                    self.saveAnnotationTypeTree()
                    # 让表自适应内容长度
                    self.annotationTypeTree.resizeColumnToContents(0)
                    self.annotationTypeTree.resizeColumnToContents(1)
                else:
                    QMessageBox.warning(self, '警告', "该颜色或文本已被添加！")

    # 删除上面表格的类别
    def delete_annotationTypeItem(self):
        items = self.annotationTypeTree.selectedItems()
        for item in items:
            # TODO:如果删除的类别已被使用，则无法删除
            existed_type = []
            for name, annotation in self.Annotations.items():
                existed_type.append(annotation['type'])
            if item.text(0) in existed_type:
                QMessageBox.warning(self, '警告', '无法删除已存在的标注类型！')
                return
            self.AnnotationTypes.pop(item.text(0))
            self.saveAnnotationTypeTree()
            (item.parent() or self.annotationTypeTree.invisibleRootItem()).removeChild(item)

    # 修改上面表格的类别
    def changeCategory(self):
        current_item = self.annotationTypeTree.currentItem()
        if current_item:
            current_type = current_item.text(0)
            current_color = self.AnnotationTypes[current_type]
            dialog = ChangeTypeDialog()
            if dialog.exec_() == QDialog.Accepted:
                new_type = dialog.get_text()
                if new_type and new_type not in self.AnnotationTypes.keys():
                    current_item.setText(0, new_type)
                    self.AnnotationTypes = update_dict_key(self.AnnotationTypes, current_type, new_type)
                    # 保存
                    self.saveAnnotationTypeTree()

                    # 遍历一遍annotationTree
                    for row in range(self.annotationTree.topLevelItemCount()):
                        item = self.annotationTree.topLevelItem(row)
                        type = item.text(1)
                        if type == current_type:
                            item.setText(1, new_type)
                            self.Annotations[f'标注{row}']['type'] = new_type
                            self.changeAnnotaionSignal.emit(row, new_type, current_color)

    # 更改标注颜色
    def changeAnnotationColor(self):
        new_color = QColorDialog.getColor(QColor(0, 0, 0), self, "选择颜色")
        if new_color.isValid():
            if list(new_color.getRgb()) not in self.AnnotationTypes.values():
                current_item = self.annotationTypeTree.currentItem()
                if current_item:
                    # 将图像块颜色替换
                    current_type = current_item.text(0)
                    current_color = self.AnnotationTypes[current_type]
                    pixmap = QPixmap(20, 20)
                    pixmap.fill(new_color)
                    current_item.setIcon(1, QIcon(pixmap))
                    # 更换到类别的颜色
                    self.AnnotationTypes[current_type] = list(new_color.getRgb())

                    # 重新绘制该颜色的标注
                    # 遍历一遍annotationTree
                    for row in range(self.annotationTree.topLevelItemCount()):
                        item = self.annotationTree.topLevelItem(row)
                        type = item.text(1)
                        if type == current_type:
                            item.setIcon(3, QIcon(pixmap))
                            self.Annotations[f'标注{row}']['color'] = list(new_color.getRgb())
                            self.changeAnnotaionSignal.emit(row, current_type, list(new_color.getRgb()))
                    self.showAnnotationSignal.emit(True)
                    self.set_activate_color_action()
                    if current_color == self.annotation_color:
                        self.annotation_color = list(new_color.getRgb())
                        self.annotationTypeChooseSignal.emit(self.annotation_type, self.annotation_color)
            else:
                QMessageBox.warning(self, "警告", "该颜色已被使用！")

    # 双击annotationTypeTree，如果点击的是名字，则修改标注的名称，如果点的是颜色，则修改标注的颜色
    def changeAnnotationTypeEvent(self, item, colum):
        if colum == 0:
            self.changeCategory()
        else:
            self.changeAnnotationColor()

    # 获取被点击的Tree item所在的行,并设置标注工具的颜色
    def onClickedTreeItemRow(self, item, colum):
        row = self.annotationTypeTree.indexOfTopLevelItem(item)
        self.set_AnnotationColor(row)

    # 右击AnnotationTree，弹出删除标注与修改标注的action
    def show_annotationTree_menu(self, pos):
        item = self.annotationTree.itemAt(pos)
        if item is not None:
            self.onClickedAnnotationTree(item)
            self.annotationTree_menu.exec_(self.annotationTree.mapToGlobal(pos))

    # 选择标注的颜色
    # i表示在AnnotationTree中的第几行
    def set_AnnotationColor(self, i):
        num_types = self.annotationTypeTree.topLevelItemCount()
        if i < num_types and i >= 0:
            self.annotation_flag = i
            self.annotation_type = self.annotationTypeTree.topLevelItem(i).text(0)
            self.annotation_color = self.AnnotationTypes[self.annotation_type]
            # 发送信号到TOOLManager
            self.annotationTypeChooseSignal.emit(self.annotation_type, self.annotation_color)
            self.annotationActionCheckSignal.emit(i)
            print("当前选择的标注颜色是：", self.annotation_type, self.annotation_color)


    # 标注模式切换(移动，固定矩形，矩形……)
    def set_annotation_mode(self, mode):
        self.mode = mode
        # 发送模式切换信号
        self.toolChangeSignal.emit(mode)

    def set_move_mode(self):
        self.mode = 1
        self.toolChangeSignal.emit(1)

    # 设置工具栏中的图块颜色
    def set_activate_color_action(self):
        self.AnnotationTypeChangeSignal.emit(self.AnnotationTypes)

    # 在idx处插入annotation
    def addAnnotation(self, annotation, idx, choose=True, show=False):
        """
        :param annotation: 标注的信息
        :param idx: 标注的索引
        :param choose: 是否要将该标注激活，可以用于删除，修改
        :param show: 是否要将Annotation传给ToolManager
        :return:
        """
        self.Annotations[f"标注{idx}"] = annotation
        item = QTreeWidgetItem(self.annotationTree)
        item.setText(0, f"标注{idx}")
        item.setText(1, annotation['type'])
        item.setText(2, annotation['tool'])
        pixmap = QPixmap(20, 20)
        color = QColor(*annotation['color'])
        pixmap.fill(color)
        item.setIcon(3, QIcon(pixmap))
        description = annotation.get('description')
        if description is not None:
            item.setText(4, description)
        # 让表自适应内容长度
        self.annotationTree.resizeColumnToContents(0)
        self.annotationTree.resizeColumnToContents(1)
        self.annotationTree.resizeColumnToContents(2)
        self.annotationTree.resizeColumnToContents(3)
        self.annotationTree.resizeColumnToContents(4)
        # 设置选中状态
        if choose:
            self.annotationTree.setCurrentItem(item)
            self.choosed_idx = idx
        # 是否要将信息传给ToolManager
        if show:
            self.syncAnnotationSignal.emit(annotation.copy(), idx, self.choosed_idx if self.choosed_idx is not None else -1)

    # 激活当前标注，并且将控制点绘画出来
    def onClickedAnnotationTree(self, item):
        self.annotationTree.setCurrentItem(item)
        self.choosed_idx = self.annotationTree.indexOfTopLevelItem(item)
        # 将当前的choosed_idx与ToolManager的同步
        self.updateChoosedItemSignal.emit(self.choosed_idx)

    # 修改当前标注,并将标注的信息与ToolManager同步
    def changeAnnotation(self):
        current_item = self.annotationTree.currentItem()
        if current_item:
            # 获取当前标注的索引
            row_idx = self.annotationTree.indexOfTopLevelItem(current_item)
            old_type = current_item.text(0)
            dialog = ChangeAnnotationDiaglog(self.AnnotationTypes, old_type)
            if dialog.exec_() == QDialog.Accepted:
                new_type = dialog.get_text()
                new_color = self.AnnotationTypes[new_type]
                # 修改self.Annotation与ToolManager中的
                if new_type != old_type:
                    self.Annotations[f'标注{row_idx}']['type'] = new_type
                    self.Annotations[f"标注{row_idx}"]['color'] = new_color
                    current_item.setText(1, new_type)
                    pixmap = QPixmap(20, 20)
                    color = QColor(*new_color)
                    pixmap.fill(color)
                    current_item.setIcon(3, QIcon(pixmap))
                    # 将idx、类型、颜色发送给ToolManger
                    self.changeAnnotaionSignal.emit(row_idx, new_type, new_color)
        else:
            QMessageBox.warning(self, '警告', '请先选择要修改的标注')

    # 删除掉当前的标注
    def deleteAnnotation(self):
        current_item = self.annotationTree.currentItem()
        if current_item:
            # 获取当前标注的索引
            row_idx = self.annotationTree.indexOfTopLevelItem(current_item)
            dialog = AffirmDialog("是否要删除该标注？")
            if dialog.exec_() == QDialog.Accepted:
                self.annotationTree.clearSelection()
                self.choosed_idx = None
                self.Annotations = delDictItem(self.Annotations, row_idx)
                # 删除Tree中的元素
                item_to_remove = self.annotationTree.topLevelItem(row_idx)
                self.annotationTree.takeTopLevelItem(self.annotationTree.indexOfTopLevelItem(item_to_remove))
                # 遍历并修改每一行
                for i in range(self.annotationTree.topLevelItemCount()):
                    item = self.annotationTree.topLevelItem(i)
                    name = item.text(0)
                    old_idx = int(re.search(r'\d+', name).group())
                    if old_idx > row_idx:
                        item.setText(0, f"标注{old_idx-1}")
                # 将idx发送给ToolManager，并对key进行重命名
                self.deleteAnnotationSignal.emit(row_idx)

        else:
            QMessageBox.warning(self, '警告', '请先选择要删除的标注')

    # 填写对标注的描述
    def set_description(self, item, column):
        if column == 4:
            self.editItem(item, column)

    def editItem(self, item, column):
        self.annotationTree.openPersistentEditor(item, column)
        editor = self.annotationTree.itemWidget(item, column)
        if isinstance(editor, QLineEdit):
            editor.selectAll()
            editor.returnPressed.connect(lambda: self.closeEditor(item, column))
            # 捕获焦点丢失事件
            editor.editingFinished.connect(lambda: self.closeEditor(item, column))
            # editor.focus().connect(lambda: self.closeEditor(item, column))

    def closeEditor(self, item, column):
        editor = self.annotationTree.itemWidget(item, column)
        self.annotationTree.closePersistentEditor(item, column)
        if isinstance(editor, QLineEdit):
            item.setText(column, editor.text())
        description = item.text(column)
        if description != '':
            row_idx = self.annotationTree.indexOfTopLevelItem(item)
            self.Annotations[f'标注{row_idx}']['description'] = description

    # 删除所有的标注
    def clearAnnotations(self):
        if self.Annotations:
            dialog = AffirmDialog("是否要删除所有标注？")
            if dialog.exec_() == QDialog.Accepted:
                rows = self.annotationTree.topLevelItemCount()
                # 从下至上进行删除
                self.choosed_idx = None
                for row in range(rows-1, -1, -1):
                    item_to_remove = self.annotationTree.topLevelItem(row)
                    self.annotationTree.setCurrentItem(item_to_remove)
                    self.annotationTree.clearSelection()
                    self.Annotations = delDictItem(self.Annotations, row)
                    # 删除Tree中的元素
                    self.annotationTree.takeTopLevelItem(self.annotationTree.indexOfTopLevelItem(item_to_remove))
                    # 将idx发送给ToolManager，并对key进行重命名
                    self.deleteAnnotationSignal.emit(row)

    # 设置当前slide的路径
    def set_slide_path(self, slide_path):
        self.slide_path = slide_path

    def set_annotation_file_dir(self):
        self.annotation_file_dir = self.folderselector.FileDir()

    def loadAnnotation(self):
        options = QFileDialog.Options()
        path, _ = QFileDialog.getOpenFileName(self, "选择标注文件", self.annotation_file_dir,
                                                        "标注 (*.json)", options=options)
        if not os.path.exists(path):
            return
        # 如果当前存在标注，则询问是否要保存标注，再将self.Annotation清除
        if self.Annotations:
            dialog = AffirmDialog("是否要保存当前的标注？")
            # 保存标注
            if dialog.exec_() == QDialog.Accepted:
                self.saveAnnotations()
            # 清除当前视图，将Annotations中的清除
            self.clearAnnotationSignal.emit(True)

            # 清除当前的标注
            self.annotationTree.clear()
            self.choosed_idx = None

        with open(path, 'r') as f:
            file = json.load(f)
            f.close()
        slide_name, _ = os.path.splitext(os.path.basename(self.slide_path))
        if slide_name not in file['image_path']:
            QMessageBox.warning(self, '警告', '标注与图片不匹配！')
            return
        # 更新所有的定义的类别
        self.AnnotationTypes = file['color_and_type']
        self.annotationTypeTree.clear()
        self.init_AnnotationTypeTree()
        self.Annotations = OrderedDict(file['annotation'])
        # 同步更新ToolManager
        for idx, (name, annotation) in enumerate(self.Annotations.items()):
            self.addAnnotation(annotation, idx, choose=False, show=True)
        # 将导入的标注显示出来
        self.showAnnotationSignal.emit(True)
        # 将类别json保存
        self.saveAnnotationTypeTree()

    # 在标注模式下载入细胞核分割结果
    def load_nuclei(self):
        options = QFileDialog.Options()
        path, _ = QFileDialog.getOpenFileName(self, "选择标注文件", self.annotation_file_dir,
                                              "标注 (*.pkl)", options=options)
        slide_name, _ = os.path.splitext(os.path.basename(self.slide_path))
        if os.path.exists(path):
            if slide_name in path:
                self.loadNucleiAnnSignal.emit(path)
            else:
                QMessageBox.warning(self, '警告', '导入文件与当前图片不符')

    # 反转细胞核显示按钮
    def reverse_btn(self):
        if self.showNucleiAnn_btn.text() == "显示细胞核":
            self.showNucleiAnn_btn.setText("不显示细胞核")
        else:
            self.showNucleiAnn_btn.setText("显示细胞核")

    # 保存标注
    def saveAnnotations(self):
        if self.Annotations:
            self.saveAnnotationTypeTree()
            slide_name, _ = os.path.splitext(os.path.basename(self.slide_path))
            os.makedirs('annotations', exist_ok=True)
            options = QFileDialog.Options()
            path, _ = QFileDialog.getSaveFileName(self, '保存标注',
                                                  f'./annotations/{slide_name}_annotation.json',
                                                  'json Files(*.json)', options=options)
            if path:
                annotation = {"image_path": self.slide_path,
                              "color_and_type": self.AnnotationTypes,
                              "annotation": self.Annotations}
                with open(path, 'w') as f:
                    f.write(json.dumps(annotation, indent=2, ensure_ascii=False))
                    f.close()
                # 发送细胞核pkl结果要保存的路径
                self.saveNucleiAnnSignal.emit(path.replace('json', 'pkl'))
        else:
            QMessageBox.warning(self, '警告', '当前没有标注')


    def modifyAnnotation(self, annotation, choosed_idx):
        self.Annotations[f"标注{choosed_idx}"] = annotation

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AnnotationWidget()
    window.show()
    sys.exit(app.exec_())