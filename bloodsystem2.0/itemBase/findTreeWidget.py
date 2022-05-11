# encoding: utf-8
"""
@author: red0orange
@file: findTreeWidget.py
@time:  下午7:25
@desc:
"""
from itemBase.treeWidget import *
from functools import partial

from utils.utils import *


class FindTreeWidget(TreeWidget):
    star_items_signal = pyqtSignal(list)
    def __init__(self, parent):
        super(FindTreeWidget, self).__init__(parent)
        self.star_action = QAction('标记文件')
        self.menu.addAction(self.star_action)
        self.setHeaderHidden(True)
        pass

    def init(self, file_tree):
        "从全文件tree复制一个副本过来且全部设置为隐藏"
        children = get_children(file_tree)
        protect_int(children)
        self.addTopLevelItems([child.clone() for child in children])
        self.traverse(lambda item: item.setHidden(False))
        self.set_root(file_tree.root)
        pass

    def show_tag_items(self, tag_items):
        for key, items in tag_items.items():
            top_item = QTreeWidgetItem(self, [key, 'tag'])
            top_item.addChildren(items)

    def show_find_items(self, find_text):
        # TODO 目前只支持全名称对应搜索，差别一点都搜不到
        self.traverse(partial(self.show_special_name_items, names=[find_text]))
        return True

    @staticmethod
    def show_special_name_items(item: QTreeWidgetItem, names):
        item.setHidden(True)
        for name in names:
            if item.text(0) in name:
                item.setHidden(False)
                for i in TreeWidget.get_parents(item):
                    i.setHidden(False)
        pass

    def deal_actions(self, action):
        super(FindTreeWidget, self).deal_actions(action)
        if action == self.star_action:
            current_items = self.selectedItems()
            for item in current_items:
                pass
            self.star_items_signal.emit(current_items)

