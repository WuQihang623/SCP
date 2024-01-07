import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTabWidget

from UI.UI_annotation import UI_Annotation
from UI.UI_Control import UI_Controller

class Controller(QTabWidget):
    def __init__(self):
        super().__init__()
        self.annotation_widget = UI_Annotation()
        self.controller_widget = UI_Controller()
        self.addTab(self.annotation_widget, "标注桌面")
        self.addTab(self.controller_widget, "可视化桌面")
    def load_annotation(self):
        """
            载入标注文件
        """

    def add_label_category(self):
        """
            增加标注工具的类别，肿瘤区域，基质区域，角化物……
        """

    def remove_label_category(self):
        """
            删除标注类别
            先要获取到当前被选中的标注类别，然后更新标注类别字典
        """

    def change_label_tool(self):
        """
            切换当前的标注工具，切换成： 矩形，多边形，测量工具……
            通过点击标注工具
        """

    def change_label_category(self):
        """
            切换当前标注工具的类型，切换成：肿瘤区域，基质区域……
            通过点击添加的label
        """

    def change_label_color(self):
        """
            更换添加的类别的颜色
            通过双击添加的label
        """

    def change_label_name(self):
        """
            更换添加的类别的名称，
            通过双击添加的label
        """

    def add_annotation(self):
        """
            绘制完成一个标注后，将标注结果记录下来
        """

    def remove_annotation(self):
        """
            删除绘制好的标注
            先获取到被点击的标注，然后删除记录以及场景中的图元
        """

    def modify_annotation(self):
        """
            修改绘制好的标注
            先获取被点击的标注，然后更新标注字典以及场景中的图元
        """

    def save_annotation(self):
        """
            保存标注
        """

    def clear_annotaiton(self):
        """
            清空标注
        """


    """
        结果文件的格式
        Args: {
            "properties": {
                "nucleus_info": {
                    "肿瘤细胞": {"type": 1, "color": [255, 0, 0], "number": 1000},
                    "淋巴细胞": {"type": 2, "color": [0, 255, 0], "number": 1000},
                    "中性粒细胞": {"type": 3, "color": [255, 255, 0], "number": 1000},
                    "基质细胞": {"type": 4, "color": [0, 0, 255], "number": 1000},
                },
                "nucleus_diff_info": {
                    "FN": {"color": [255, 0, 0]},
                    "FP": {"color": [0, 255, 0]},
                }
                "heatmap_info": {
                    "heatmap": ["组织区域热力图", "边界区域热力图"],
                    "downsample": int,
                },
                "contour_info": {
                    "肿瘤区域": {"color": [255, 0, 0], "type": 1},
                    "基质区域": {"color": [0, 255, 0], "type": 2},
                    "图像块": {"color": [0, 0, 0], "type": 3}
                }
            }
            "nucleus_info": {
                "type": ndarray,
                "center": ndarray,
                "contour": ndarray,
            },
            "nucleus_diff_info": {
                "center": ndarray,
                "diff_array": ndarray = ["TP", "TN", "FP", "FN", ...]
            },
            "heatmap_info": {
                "组织区域热力图": ndarray,
                "边界区域热力图": ndarray,
            }
            "contour_info": {
                "contour": ndarray,  array[array(contour1), array(contour2), ...]
                "type": ndarray, array[1, 2, 3, ...]
            }
            
        }
    """
    def load_nucleus(self):
        """
            载入细胞核结果文件
        """

    def show_nucleus(self):
        """
            显示/关闭细胞核分割结果
            选择要显示哪些细胞核
        """

    def load_heatmap(self):
        """
            载入热力图
        """

    def show_heatmap(self):
        """
            显示/关闭热力图
            选择要显示哪些热力图
        """

    def load_contour(self):
        """
            载入轮廓文件
            选择要显示哪些轮廓
        """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Controller()
    window.show()
    sys.exit(app.exec_())