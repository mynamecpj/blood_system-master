# encoding: utf-8
"""
@author: Soshio
@file: fileTreeWidget.py
@time:  下午1:56
@desc:
"""
from PyQt5 import Qt, QtGui
from PyQt5.QtWidgets import QWidget, QTreeWidget, QTreeWidgetItem, QComboBox, QStackedWidget, QMenu, QAction, \
    QAbstractItemView
from PyQt5.QtCore import QFileInfo, Qt, pyqtSignal, QThread, QObject

from itemBase.treeWidget import *
from utils.fileAlgorithm import *
from functools import partial
from pathlib import Path
import os


class Loader(QObject):
    load_finish_signal = pyqtSignal()

    def __init__(self):
        super(Loader, self).__init__(parent=None)
        pass

    def load_project_structure(self, tree, startpath):
        Loader._load_project_structure(tree, startpath)
        self.load_finish_signal.emit()
        pass

    @staticmethod
    def _load_project_structure(tree, startpath):
        paths = [os_path_join(startpath, element) for element in os.listdir(startpath)]
        paths = sorted(paths, key=lambda item: os.path.isdir(item), reverse=True)  # 排序文件夹和文件
        for path in paths:
            if os.path.isdir(path):
                fileInfo = QFileInfo(path)
                parent_itm = QTreeWidgetItem(tree, [fileInfo.fileName(), 'folder'])
                parent_itm.setIcon(0, QtGui.QIcon(QFileIconProvider().icon(fileInfo)))
                Loader._load_project_structure(parent_itm, path)
            else:
                fileInfo = QFileInfo(path)
                parent_itm = QTreeWidgetItem(tree, [fileInfo.fileName(), 'file'])
                parent_itm.setIcon(0, QtGui.QIcon(QFileIconProvider().icon(fileInfo)))


class FileTreeWidget(TreeWidget):
    star_items_signal = pyqtSignal(list)
    load_project_structure_signal = pyqtSignal(QTreeWidget, str)

    def __init__(self, parent):
        super(FileTreeWidget, self).__init__(parent)
        self.star_action = QAction('标记文件')
        self.menu.addAction(self.star_action)
        self.setHeaderHidden(True)

        # 子树
        self.other_tree_widgets = None
        # 加载文件树的线程
        self.loader_thread = QThread()
        self.loader = Loader()
        self.loader.moveToThread(self.loader_thread)
        self.loader_thread.start()
        # 信号连接必须在start之后，否则槽函数仍在主线程运行，原因应该是start之后那个object才真正到另外一个线程
        self.load_project_structure_signal.connect(self.loader.load_project_structure)
        self.loader.load_finish_signal.connect(self.init_other_tree_widget)
        pass

    def set_other_tree_widgets(self, other_tree_widgets: list):
        # 设置子树
        self.other_tree_widgets = other_tree_widgets
        pass

    def init_other_tree_widget(self):
        # 子树的意为每次文件树初始化也要带动它们初始化
        for tree in self.other_tree_widgets:
            tree.init(self)
        self.setEnabled(True)
        [i.setEnabled(True) for i in self.other_tree_widgets]
        pass

    def load_project_structure(self, startpath):
        "加载某个文件夹作为根目录"
        self.set_root(startpath)
        self.setEnabled(False)
        [i.setEnabled(False) for i in self.other_tree_widgets]
        self.load_project_structure_signal.emit(self, startpath)
        pass

    # def get_index_tree(self, all_indexes):
    #     return get_index_tree(all_indexes)

    def deal_actions(self, action):
        super(FileTreeWidget, self).deal_actions(action)
        if action == self.star_action:
            current_items = self.selectedItems()
            for item in current_items:
                # TODO 改颜色
                pass
            current_indexes = [self.item_index_of_item(item) for item in current_items]
            self.star_items_signal.emit(current_indexes)

    def get_same_name_items(self):
        "找到同名文件，暂时打算显示在另一个特殊的TreeWidget里面"
        result = {}
        items = self.findItems('file', Qt.MatchContains | Qt.MatchRecursive, 1)
        file_paths = [self.get_full_path(item) for item in items]
        _, same_paths = find_same_name_file(file_paths)
        same_items = {}  # key + list包含相同的文件名
        for key, paths in same_paths.items():
            indexs = []
            for path in paths:
                indexs.append(file_paths.index(path))
            same_items[key] = [items[index] for index in indexs]
        for key, items in same_items.items():
            top_level_items = self.get_top_level_items_clone_by_items(items)
            result[key] = top_level_items
        return result

    def show_not_labeled_imgs(self):
        items = self.findItems('file', Qt.MatchContains | Qt.MatchRecursive, 1)
        image_items = []
        xml_items = []
        xml_names = []
        img_suffix = get_image_extensions()
        xml_suffix = ['.xml']
        for item in items:
            base_name = item.text(0)
            if Path(base_name).suffix in img_suffix:
                image_items.append(item)
            elif Path(base_name).suffix in xml_suffix:
                xml_items.append(item)
                xml_names.append(base_name.split('.')[0])
        unlabeled_items = []
        for image_item in image_items:
            if image_item.text(0).split('.')[0] not in xml_names:
                unlabeled_items.append(image_item)
        self.traverse(partial(self.select_special_items, special_items=unlabeled_items))
        pass

    def get_top_level_items_clone_by_items(self, items):
        result_top_level_items = []
        parent_items = []
        for i in range(len(items)):
            parent_items += [items[i], *self.get_parents(items[i])]
        all_indexes = [self.item_index_of_item(item) for item in parent_items]
        top_level_item_indexes = [indexes[0] for indexes in all_indexes]
        unique_top_level = list(set(top_level_item_indexes))
        for top_level_index in unique_top_level:
            top_level_item = self.topLevelItem(top_level_index).clone()
            protect_items = []
            for indexes in all_indexes:
                if indexes[0] == top_level_index:
                    protect_items.append(get_index_item(top_level_item, indexes[1:]))
            rest_items = []
            for protect_item in protect_items:
                rest_items.extend([protect_item, *self.get_parents(protect_item)])
            traverse(top_level_item, partial(delete_other_items, rest_items=rest_items))
            result_top_level_items.append(top_level_item)
        return result_top_level_items

    def find_items_by_paths(self, paths):
        basenames = [os.path.basename(path) for path in paths]
        file_items = self.get_tag_items('file', recurse=True)
        file_paths = [self.get_full_path(item) for item in file_items]
        filter_file_indexes = [file_paths.index(path) for path in file_paths if os.path.basename(path) in basenames]
        result_items = [file_items[i] for i in filter_file_indexes]
        result_indexes = [self.item_index_of_item(item) for item in result_items]
        return result_indexes

# def file_name(path):
#     return os.listdir(path)
#
#
# class FileTreeWidget(TreeWidget):
#
#     def __init__(self, parent):
#         super(FileTreeWidget, self).__init__(parent)
#         self.parent = self.parentWidget()
#         self.setHeaderHidden(True)
#         self.load()
#
#     def load(self):
#         config = Config()
#         path = config.rootpath
#         dirs = file_name(path)
#         fileInfo = Qt.QFileInfo(path)
#         fileIcon = Qt.QFileIconProvider()
#         icon = QtGui.QIcon(fileIcon.icon(fileInfo))
#         root = QTreeWidgetItem(self)
#         root.setText(0, path.split('/')[-1])
#         root.setIcon(0, QtGui.QIcon(icon))
#         self.CreateTree(dirs, root, path)
#
#     def CreateTree(self, dirs, root, path):
#         for i in dirs:
#             path_new = path + '/' + i
#             if os.path.isdir(path_new):
#                 fileInfo = Qt.QFileInfo(path_new)
#                 fileIcon = Qt.QFileIconProvider()
#                 icon = QtGui.QIcon(fileIcon.icon(fileInfo))
#                 child = QTreeWidgetItem(root)
#                 child.setText(0, i)
#                 child.setIcon(0, QtGui.QIcon(icon))
#                 dirs_new = file_name(path_new)
#                 self.CreateTree(dirs_new, child, path_new)
#             else:
#                 fileInfo = Qt.QFileInfo(path_new)
#                 fileIcon = Qt.QFileIconProvider()
#                 icon = QtGui.QIcon(fileIcon.icon(fileInfo))
#                 child = QTreeWidgetItem(root)
#                 child.setText(0, i)
#                 child.setIcon(0, QtGui.QIcon(icon))

# paths = [os_path_join(startpath, element) for element in os.listdir(startpath)]
# paths = sorted(paths, key=lambda item: os.path.isdir(item), reverse=True)  # 排序文件夹和文件
# for path in paths:
#     if os.path.isdir(path):
#         parent_itm = QTreeWidgetItem(self, [os.path.basename(path), 'folder'])
#         self.addTopLevelItem(parent_itm)
#     else:
#         parent_itm = QTreeWidgetItem(self, [os.path.basename(path), 'file'])
