# encoding: utf-8
"""
@author: Soshio
@file: realTimeBase.py
@time:  下午1:56
@desc:
"""

from utils.fileAlgorithm import *
from xml.dom import minidom


class RealTimeAlgorithm:
    def __init__(self):
        pass

    @staticmethod
    def change_error_xml(new_id, new_class, idx, xml_path):
        doc = minidom.parse(xml_path)
        root = doc.documentElement
        objects = root.getElementsByTagName('object')
        for object_ in objects:
            x = object_.getElementsByTagName('x')[0].firstChild.data
            y = object_.getElementsByTagName('y')[0].firstChild.data
            x, y, = map(float, [x, y])
            if idx[0] == x and idx[1] == y:
                object_.getElementsByTagName('categories_id')[0].firstChild.data = new_id
                object_.getElementsByTagName('name')[0].firstChild.data = new_class
        with open(xml_path, 'w', encoding='utf-8') as f:
            doc.writexml(f, indent='', addindent='\t', newl='\n', encoding='utf-8')
        pass

    @staticmethod
    def delete_image_by_time(path, time: str):
        """删除给的文件列表中文件名包含time的文件"""
        files = get_dir_all_file(path)
        for file in files:
            if time in os.path.basename(file):
                os.remove(file)

        pass


if __name__ == '__main__':
    new_class = '血小板'
    idx = [0.283, 0.252, 5]
    xml_path = 'D:\Blood\SU\\thosix\\root\小明-男-21-299\\xmls\\158400007.xml'
    RealTimeAlgorithm.change_error_xml(new_class, idx, xml_path)
