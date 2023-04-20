# 改变字典的key但不改变顺序
import re
from collections import OrderedDict

def delDictItem(annotation_dict, del_idx):
    i = 0
    new_annotation_dict = OrderedDict()
    for key, item in annotation_dict.items():
        num = int(re.search(r'\d+', key).group())
        assert num == i
        i += 1
        if num < del_idx:
            new_annotation_dict[key] = item
        elif num > del_idx:
            new_annotation_dict[f"标注{num-1}"] = item
    return new_annotation_dict



