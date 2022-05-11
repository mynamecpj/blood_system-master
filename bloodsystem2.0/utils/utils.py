# encoding: utf-8
"""
@author: red0orange
@file: utils.py
@time:  上午12:05
@desc:
"""
import cv2
from .fileAlgorithm import *
import numpy as np


def protect_int(value):
    "尝试将value从str转成int，若无法转换则返回原来的value"
    result = value
    if isinstance(value, str):
        if value.isnumeric():
            result = int(value)
    return result


def listy(value):
    if isinstance(value, list):
        return value
    elif isinstance(value, set):
        return list(value)
    else:
        return [value]


def replace_suffix(path, new_suffix):
    return os_path_join(os_path_dirname(path), os.path.basename(path).split('.')[-2])


def get_short_path(full_path: str, root_path: str):
    full_path_list = full_path.split('/')
    root_path_list = root_path.split('/')
    short_path = ''

    for i in range(len(root_path_list)):
        full_path_list.remove(full_path_list[0])

    for i in full_path_list:
        short_path += '/' + str(i)
    short_path = 'root' + short_path

    return short_path


def cv_imread(file_path):
    cv_img = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)
    return cv_img

def countFile(dir):
    tmp = 0
    for item in os.listdir(dir):
        if os.path.isfile(os.path.join(dir, item)):
            tmp += 1
        else:
            tmp += countFile(os.path.join(dir,item))
    return tmp