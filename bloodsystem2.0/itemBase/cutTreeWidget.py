# encoding: utf-8
"""
@author: red0orange
@file: fileTreeWidget.py
@time:  下午7:25
@desc: 用于产生切割图片的dialog
"""
from itemBase.treeWidget import *
from utils.fileAlgorithm import *
from functools import partial
from pathlib import Path
import os
from utils.utils import *


def get_index_tree(all_indexes):
    index_tree = Tree()
    index_tree.value = -1
    for indexes in all_indexes:
        current_node = index_tree
        for layer in indexes:
            if layer not in [child.value for child in current_node.children]:
                new_node = Tree()
                new_node.value = layer
                current_node.addChild(new_node)
            current_node = current_node.findChild(lambda node: hasattr(node, 'value') and node.value == layer)
    return index_tree


class CutTreeWidget(TreeWidget):
    star_items_signal = pyqtSignal(list)

    def __init__(self, parent):
        super(CutTreeWidget, self).__init__(parent)
        self.setColumnCount(3)  # 只有设置大于Item的实际列数的str才能被搜索到
        self.setColumnHidden(1, True)  # 不显示第二列
        self.setColumnHidden(2, True)  # 不显示第三列
        self.menu.clear()
        pass

    def init(self, file_tree):
        "加载某个文件夹作为根目录"
        children = get_children(file_tree)
        protect_int(children)
        self.addTopLevelItems([child.clone() for child in children])
        self.traverse(lambda item: item.setCheckState(0, Qt.Unchecked))
        self.set_root(file_tree.root)
        pass

    def get_index_tree(self, all_indexes):
        return get_index_tree(all_indexes)

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
