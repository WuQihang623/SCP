import os
import json
import constants
import numpy as np
import openslide
from ctypes import windll
from collections import OrderedDict

# 支持读取的文件格式
def get_supported_format():
    return ["svs",  "vms", "vmu", "ndpi", "scn",
            "mrx", "tiff", "svslide", "tif",
            "bif", "mrxs", "bif", "dmetrix", "qptiff"]

def get_file_option():
    option = ""
    for format in get_supported_format():
        option += " *." + format
    return option

# 判断是否为中文路径
def is_chinese(string):
    """
    检查整个字符串是否包含中文
    :param string: 需要检查的字符串
    :return: bool
    """
    for ch in string:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True

    return False

# 判断文件是否完整
def is_file_copy_finished(file_path):
    finished = False
    GENERIC_WRITE         = 1 << 30
    FILE_SHARE_READ       = 0x00000001
    OPEN_EXISTING         = 3
    FILE_ATTRIBUTE_NORMAL = 0x80
    file_path_unicode = file_path
    h_file = windll.Kernel32.CreateFileW(file_path_unicode, GENERIC_WRITE, FILE_SHARE_READ, None, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, None)
    if h_file != -1:
        windll.Kernel32.CloseHandle(h_file)
        finished = True
        try:
            openslide.open_slide(file_path)
        except:
            return False
    return finished

# 判断WSI路径是否包含中文，WSI文件是否损坏
def judge_slide_path(slide_path):
    if is_chinese(slide_path):
        return "图片无法打开，路径包含中文字符！"
    elif slide_path == '':
        return None
    elif not os.path.exists(slide_path):
        return "图片路径不存在！"
    else:
        try:
            if is_file_copy_finished(slide_path) is False:
                return "图片文件不完整，无法打开！"
            else:
                return True
        except:
            return "图片文件损坏，无法打开！"

# 用于更新有序字典的key
def update_dict_key(d, old_key, new_key):
    """
    将字典中的某个键名 old_key 更改为 new_key，但不改变字典顺序

    :param d: 原始字典
    :param old_key: 要更改的键名
    :param new_key: 更改后的键名
    :return: 更改后的字典
    """
    # 创建一个新的有序字典
    new_dict = OrderedDict()

    # 遍历原始字典中的键值对，将键名为 old_key 的键名修改为 new_key，其余键值对不变
    for k, v in d.items():
        if k == old_key:
            new_dict[new_key] = v
        else:
            new_dict[k] = v
    return new_dict

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)

# 读取缓存文件，即存放结果的路径
def setResultFileDir(mode=1):
    json_path = f'{constants.cache_path}/cache_dir.json'
    if not os.path.exists(json_path):
        return "./"

    with open(json_path, 'r') as f:
        data = json.load(f)
        f.close()

    if mode == 1:
        path = data.get("anno_dir")
    elif mode == 2:
        path = data.get("result_dir")
    elif mode == 3:
        path = data.get("slide_dir")
    else:
        return "./"
    path = "./" if path is None else path
    return path

# 写缓存文件，即存放结果的路径
def saveResultFileDir(path, mode):
    json_path = f'{constants.cache_path}/cache_dir.json'
    data = {}
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            data = json.load(f)
            f.close()
    if mode == 1:
        data["anno_dir"] = path
    elif mode == 2:
        data["result_dir"] = path
    elif mode == 3:
        data["slide_dir"] = path
    elif mode == 4:
        data["slide_info"] = path
    with open(json_path, 'w') as f:
        f.write(json.dumps(data))
        f.close()

def setFileWatcherDir():
    if os.path.exists(f'{constants.cache_path}/filewatcher_dir.json'):
        with open(f'{constants.cache_path}/filewatcher_dir.json', 'r') as f:
            path = json.load(f)
            f.close()
        if os.path.exists(path):
            return path
        else:
            return None
    else:
        return None

def saveFileWatcherDir(path):
    with open(f'{constants.cache_path}/filewatcher_dir.json', 'w') as f:
        f.write(json.dumps(path))
        f.close()
