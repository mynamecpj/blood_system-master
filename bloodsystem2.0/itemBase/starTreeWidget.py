# encoding: utf-8
"""
@author: red0orange
@file: starTreeWidget.py
@time:  下午3:39
@desc:
"""
from itemBase.treeWidget import *
from functools import partial
from pathlib import Path
import os

from utils.utils import *


class StarTreeWidget(TreeWidget):
    def __init__(self, parent):
        super(StarTreeWidget, self).__init__(parent)
        self.items = []
        self.cancel_star_action = QAction('取消标记该文件')
        self.menu.addAction(self.cancel_star_action)
        self.setHeaderHidden(True)
        pass

    def init(self, file_tree):
        "从全文件tree复制一个副本过来且全部设置为隐藏"
        children = get_children(file_tree)
        protect_int(children)
        self.addTopLevelItems([child.clone() for child in children])
        self.traverse(lambda item: item.setHidden(True))
        self.set_root(file_tree.root)
        pass

    def add_items_by_indexes(self, all_indexes):
        all_indexes = listy(all_indexes)
        items = []
        for indexes in all_indexes:
            item = self.get_index_item(indexes)
            items.append(item)
        self.items.extend(self.get_leaf_items(items))
        self.traverse(partial(self.select_special_items, special_items=self.items))
        pass

    def current_star_items_path(self):
        "返回当前所有被标记的路径"
        all_file_items = [item for item in self.get_tag_items('file') if (not item.isHidden())]
        all_file_paths = [self.get_full_path(item) for item in all_file_items]
        return all_file_paths

    def deal_actions(self, action):
        super(StarTreeWidget, self).deal_actions(action)
        if action == self.cancel_star_action:
            current_items = self.selectedItems()
            for item in current_items:
                item.setHidden(True)
            for item in self.get_leaf_items(current_items):
                if item in self.items:
                    self.items.remove(item)
