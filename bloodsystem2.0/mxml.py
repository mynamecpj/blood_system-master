# encoding: utf-8
"""
@author: red0orange
@file: mxml.py
@time:  下午7:25
@desc: 用于产生切割图片的dialog
"""
from xml.dom import minidom
from PyQt5.QtGui import QImage, QPainterPath
from PyQt5.QtCore import QPointF
from utils.fileAlgorithm import *
import re
import os


class MXml(object):
    def __init__(self, file):
        # return result, fileLocation, int(img_width), int(img_height)
        self.boxes = None
        self.file_path = None
        self.img_width = None
        self.img_height = None
        self.patient_num = None
        self.ill_sort = None
        self.read_xml(file)
        pass

    def read_xml(self, file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            doc = minidom.parse(f)
            root = doc.documentElement

            file_path = root.getElementsByTagName('file_path')[0].firstChild.data
            patient_num = root.getElementsByTagName('patientNum')[0].firstChild.data
            # ill_sort = root.getElementsByTagName('illSort')[0].firstChild.data

            img_size = root.getElementsByTagName('img_size')[0]
            img_width = img_size.getElementsByTagName('width')[0].firstChild.data
            img_height = img_size.getElementsByTagName('height')[0].firstChild.data

            img_width, img_height = map(int, [img_width, img_height])
            self.file_path = file_path
            self.img_height = int(img_height)
            self.img_width = int(img_width)
            self.patient_num = patient_num
            # self.ill_sort = ill_sort

            boxes = []
            objects = root.getElementsByTagName('object')
            for object_ in objects:
                categories_id = object_.getElementsByTagName('categories_id')[0].firstChild.data
                name = object_.getElementsByTagName('name')[0].firstChild.data
                x = object_.getElementsByTagName('x')[0].firstChild.data
                y = object_.getElementsByTagName('y')[0].firstChild.data
                width = object_.getElementsByTagName('width')[0].firstChild.data
                height = object_.getElementsByTagName('height')[0].firstChild.data
                categories_id = int(categories_id)
                x, y, width, height = map(float, [x, y, width, height])
                boxes.append([x, y, width, height, categories_id, name])
            self.boxes = boxes

    @staticmethod
    def change_file_path(new_path: str):
        f = open(new_path, 'r')
        xmldata = f.read()
        xmldata = re.sub('\<file_path>(.*?)\</file_path>', '<file_path>{}</file_path>'.format(new_path), xmldata)
        f.close()
        f = open(new_path, 'w')
        f.write(xmldata)
        f.close()
        pass

    @staticmethod
    def get_xml(img_path, items, scene, save_path):
        img_path = img_path.replace('\\', '/')
        img_width, img_height = QImage(img_path).size().width(), QImage(img_path).size().height()
        x_proportion = img_width / scene.width()
        y_proportion = img_height / scene.height()

        doc = minidom.Document()
        annotation = doc.createElement('annotation')
        doc.appendChild(annotation)

        file_path = doc.createElement('file_path')
        file_path.appendChild(doc.createTextNode(img_path))
        annotation.appendChild(file_path)

        OneDirname = doc.createElement('patientNum')  # 上一级的目录名
        OneDirname.appendChild(doc.createTextNode(os_path_dirname(img_path).split('/')[-1]))
        # TwoDirname = doc.createElement('illSort')  # 上二级的目录名
        # TwoDirname.appendChild(doc.createTextNode(os_path_dirname(img_path).split('/')[-2]))
        annotation.appendChild(OneDirname)
        # annotation.appendChild(TwoDirname)

        size = doc.createElement('img_size')
        annotation.appendChild(size)
        width = doc.createElement('width')
        width.appendChild(doc.createTextNode('{}'.format(img_width)))
        height = doc.createElement('height')
        height.appendChild(doc.createTextNode('{}'.format(img_height)))
        size.appendChild(width)
        size.appendChild(height)
        xs, ys, widths, heights, names, ids = [], [], [], [], [], []
        for ii, item in enumerate(items):
            ids.append(item.categories_id)
            names.append(item.text)
            xs.append(item.scenePos().x() * x_proportion)
            ys.append(item.scenePos().y() * y_proportion)
            widths.append(item.width * x_proportion)
            heights.append(item.height * y_proportion)

        for x_, y_, width_, height_, name_, id_ in zip(xs, ys, widths, heights, names, ids):
            _object = doc.createElement('object')
            annotation.appendChild(_object)

            x_, width_ = map(lambda i: '{:.3}'.format(i / img_width), [x_, width_])
            y_, height_ = map(lambda i: '{:.3}'.format(i / img_height), [y_, height_])
            categories_id = doc.createElement('categories_id')
            categories_id.appendChild(doc.createTextNode(str(id_)))
            _object.appendChild(categories_id)
            name = doc.createElement('name')
            name.appendChild(doc.createTextNode(name_))
            _object.appendChild(name)
            x = doc.createElement('x')
            x.appendChild(doc.createTextNode(x_))
            y = doc.createElement('y')
            y.appendChild(doc.createTextNode(y_))
            width = doc.createElement('width')
            width.appendChild(doc.createTextNode(width_))
            height = doc.createElement('height')
            height.appendChild(doc.createTextNode(height_))
            _object.appendChild(x)
            _object.appendChild(y)
            _object.appendChild(width)
            _object.appendChild(height)

        if not os.path.exists(os_path_dirname(save_path)):
            os.makedirs(os_path_dirname(save_path), exist_ok=True)
        with open(save_path, 'w', encoding='utf-8') as f:
            doc.writexml(f, indent='', addindent='\t', newl='\n', encoding='utf-8')

    @staticmethod
    def export_star_xml(xml_path, img_paths):
        doc = minidom.Document()
        image_paths = doc.createElement('image_paths')
        doc.appendChild(image_paths)
        for img_path in img_paths:
            path = doc.createElement('path')
            path.appendChild(doc.createTextNode(img_path))
            image_paths.appendChild(path)
        with open(xml_path, 'w', encoding='utf-8') as f:
            doc.writexml(f, indent='', addindent='\t', newl='\n', encoding='utf-8')

    @staticmethod
    def import_star_xml(xml_path):
        result_img_paths = []
        with open(xml_path, 'r', encoding='utf-8') as f:
            dom = minidom.parse(f)
            img_paths = dom.documentElement
            paths = [img_paths.getElementsByTagName('path')[i].firstChild.data for i in
                     range(len(img_paths.getElementsByTagName('path')))]
            result_img_paths = paths
        return result_img_paths

    @staticmethod
    def modify_xml_to_correct(root_path, new_root, class_dict):
        "临时函数更改所有xml文件用于适应代码的变化"
        paths = get_files(root_path, ['.xml'], recurse=True)
        for path in paths:
            try:
                rel_path = os_path_relpath(path, root_path)
                old_path = path
                new_path = os_path_join(new_root, rel_path)
                print(old_path)
                if not os.path.isdir(os_path_dirname(new_path)):
                    os.makedirs(os_path_dirname(new_path), exist_ok=True)
                with open(old_path, 'r', encoding='utf-8') as f:
                    dom = minidom.parse(f)
                    root = dom.documentElement

                    filename = root.getElementsByTagName('filename')[0].firstChild.data
                    fileLocation_ = root.getElementsByTagName('fileLocation')[0].firstChild.data
                    relativeLocation = root.getElementsByTagName('relativeLocation')[0].firstChild.data
                    img_width_ = root.getElementsByTagName('width')[0].firstChild.data
                    img_height_ = root.getElementsByTagName('height')[0].firstChild.data

                    object = root.getElementsByTagName('object')
                    if len(object) != 1:
                        raise BaseException('xml error')
                    object = object[0]
                    names = object.getElementsByTagName('name')
                    names = [name_node.firstChild.data for name_node in names]
                    xs = object.getElementsByTagName('x')
                    xs = [x_node.firstChild.data for x_node in xs]
                    ys = object.getElementsByTagName('y')
                    ys = [y_node.firstChild.data for y_node in ys]
                    widths = object.getElementsByTagName('width')
                    widths = [width_node.firstChild.data for width_node in widths]
                    heights = object.getElementsByTagName('height')
                    heights = [hegiht_node.firstChild.data for hegiht_node in heights]

                # 重新写
                doc = minidom.Document()
                annotation = doc.createElement('annotation')
                doc.appendChild(annotation)

                file_path = doc.createElement('file_path')
                file_path.appendChild(doc.createTextNode(fileLocation_))
                annotation.appendChild(file_path)

                OneDirname = doc.createElement('patientNum')  # 上一级的目录名
                OneDirname.appendChild(doc.createTextNode(os_path_dirname(fileLocation_).split('/')[-1]))
                TwoDirname = doc.createElement('illSort')  # 上二级的目录名
                TwoDirname.appendChild(doc.createTextNode(os_path_dirname(fileLocation_).split('/')[-2]))
                annotation.appendChild(OneDirname)
                annotation.appendChild(TwoDirname)

                size = doc.createElement('img_size')
                annotation.appendChild(size)
                width = doc.createElement('width')
                width.appendChild(doc.createTextNode('{}'.format(img_width_)))
                height = doc.createElement('height')
                height.appendChild(doc.createTextNode('{}'.format(img_height_)))
                size.appendChild(width)
                size.appendChild(height)

                for x_, y_, width_, height_, name_ in zip(xs, ys, widths, heights, names):
                    _object = doc.createElement('object')
                    annotation.appendChild(_object)

                    # 已经错误了的名字
                    name_ = name_.replace('淋巴细胞', '幼淋巴细胞').replace('嗜酸晚幼粒细胞', '嗜酸性粒细胞') \
                        .replace('幼幼淋巴细胞', '幼淋巴细胞').replace('异型幼淋巴细胞', '幼淋巴细胞').replace('原幼稚幼淋巴细胞', '原幼稚淋巴细胞') \
                        .replace('成熟幼淋巴细胞', '成熟淋巴细胞').replace('晩幼粒细胞', '晚幼粒细胞')

                    x_, y_, width_, height_, img_width_, img_height_ = map(int, [x_, y_, width_, height_, img_width_,
                                                                                 img_height_])
                    x_, width_ = map(lambda i: '{:.3}'.format(i / img_width_), [x_, width_])
                    y_, height_ = map(lambda i: '{:.3}'.format(i / img_height_), [y_, height_])
                    categories_id = doc.createElement('categories_id')
                    categories_id.appendChild(doc.createTextNode(str(class_dict[name_])))
                    _object.appendChild(categories_id)
                    name = doc.createElement('name')
                    name.appendChild(doc.createTextNode(name_))
                    _object.appendChild(name)
                    x = doc.createElement('x')
                    x.appendChild(doc.createTextNode(x_))
                    y = doc.createElement('y')
                    y.appendChild(doc.createTextNode(y_))
                    width = doc.createElement('width')
                    width.appendChild(doc.createTextNode(width_))
                    height = doc.createElement('height')
                    height.appendChild(doc.createTextNode(height_))
                    _object.appendChild(x)
                    _object.appendChild(y)
                    _object.appendChild(width)
                    _object.appendChild(height)

                with open(new_path, 'w', encoding='utf-8') as f:
                    doc.writexml(f, indent='', addindent='\t', newl='\n', encoding='utf-8')
            except:
                print(old_path)
        pass


if __name__ == '__main__':
    all_rows = load_color_set_from_csv('class.csv')
    clsname2id = {}
    for row in all_rows:
        id = row['id']
        cls_name = row['name']
        clsname2id[cls_name] = id
    print(clsname2id)
    MXml.modify_xml_to_correct('/home/hdh/blood/data', '/home/hdh/blood/new_xml', clsname2id)
    pass
