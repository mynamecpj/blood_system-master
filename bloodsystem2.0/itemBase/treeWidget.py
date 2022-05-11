# encoding: utf-8
"""
@author: red0orange
@file: treeWidget.py
@time:  下午6:50
@desc:
"""
from PyQt5.QtWidgets import QWidget, QTreeWidget, QTreeWidgetItem, QComboBox, QStackedWidget, QMenu, QAction, \
    QAbstractItemView
from PyQt5.QtCore import QFile, Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QCursor, QColor, QBrush
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QMenu, QAction, QTreeView, QFileIconProvider
from functools import partial
from pathlib import Path
import os

from PyQt5 import QtGui

from utils import popDialogUtils
from utils.fileAlgorithm import *


def get_children(tree):
    if isinstance(tree, QTreeWidget):
        return [tree.topLevelItem(child_i) for child_i in range(tree.topLevelItemCount())]
    else:
        return [tree.child(child_i) for child_i in range(tree.childCount())]


def delete_other_items(item: QTreeWidgetItem, rest_items):
    if item.parent() is not None and item not in rest_items:
        item.parent().removeChild(item)
        item.setDisabled(True)
    pass


def traverse(tree, func):
    "对树中每个元素从上到下进行遍历并每得到一个元素都会给func函数进行处理"
    if isinstance(tree, QTreeWidget):
        children = get_children(tree)
        for child in children:
            traverse(child, func)
    else:
        func(tree)  # 调用要做事的函数
        if tree.isDisabled():
            return
        children = get_children(tree)
        for child in children:
            traverse(child, func)


def item_index_of_item(grand_parent: QTreeWidgetItem, child: QTreeWidgetItem):
    "得到child相对于grand_parent的位置索引列表，grand_parent通过一层层索引就能定位到item"
    result_index = []
    while True:
        parent = child.parent()
        if parent is None:
            if isinstance(grand_parent, QTreeWidget):
                if grand_parent.indexOfTopLevelItem(child) == -1:
                    raise BaseException('this child is not child of this grand_parent')
                result_index.append(grand_parent.indexOfTopLevelItem(child))
                break
            else:
                raise BaseException('this child is not child of this grand_parent')
        result_index.append(parent.indexOfChild(child))
        if parent == grand_parent:
            break
        child = parent
    result_index = result_index[::-1]
    return result_index


def get_index_item(grand_parent: QTreeWidgetItem, indexes: list):
    "通过索引列表得到对应位置的item"
    if isinstance(grand_parent, QTreeWidget):
        grand_parent = grand_parent.topLevelItem(indexes[0])
        indexes = indexes[1:]
    item = grand_parent
    for index in indexes:
        item = item.child(index)
    return item


class TreeWidget(QTreeWidget):
    """一个文件数的基类"""
    remove_item_signal = pyqtSignal(str)
    rename_item_signal = pyqtSignal(str, str, str)
    show_item_signal = pyqtSignal(str)

    def __init__(self, parent):
        super(TreeWidget, self).__init__(parent)
        self.root = None  # 文件树的根路径
        self.parent = parent

        self.setColumnCount(3)  # 只有设置大于Item的实际列数的str才能被搜索到
        self.setColumnHidden(1, True)  # 不显示第二列
        self.setColumnHidden(2, True)  # 不显示第三列

        self.menu = QMenu()
        self.rename_action = QAction('重命名文件', self.parent)
        self.remove_action = QAction('删除文件', self.parent)
        self.show_action = QAction('显示图片', self.parent)
        self.menu.addAction(self.remove_action)
        self.menu.addAction(self.rename_action)
        self.menu.addAction(self.show_action)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setHeaderLabels([''])

        self.customContextMenuRequested.connect(self.show_tree_widget_menu)
        pass

    def set_root(self, root_path):
        self.root = root_path
        pass

    def show_tree_widget_menu(self):
        "右键菜单阻塞处理函数"
        current_action = self.menu.exec(QCursor.pos())
        if current_action is None:
            return
        self.deal_actions(action=current_action)

    def deal_actions(self, action):
        current_items = self.selectedItems()
        if action == self.rename_action:
            if len(current_items) != 1:
                popDialogUtils.pop_warning_dialog(self.parent, '请只选择一个文件')
                return
            self.rename_item_file(current_items[0])
            pass
        elif action == self.remove_action:
            if len(current_items) != 1:
                popDialogUtils.pop_warning_dialog(self.parent, '请只选择一个文件')
                return
            self.remove_item_file(current_items[0])
            pass
        elif action == self.show_action:
            if len(current_items) != 1:
                popDialogUtils.pop_warning_dialog(self.parent, '请只选择一个文件')
                return
            if current_items[0].text(1) != 'file':
                popDialogUtils.pop_warning_dialog(self.parent, '请选择具体图片')
                return
            full_path = self.get_full_path(current_items[0])
            self.show_item_signal.emit(full_path)
        pass

    def rename_item_file(self, item):
        "重命名某个item"
        new_name = popDialogUtils.pop_text_dialog(self.parent, default_text=item.text(0))
        if new_name is None:
            return
        old_path = self.get_full_path(item)
        new_path = os_path_join(os_path_dirname(old_path), new_name)
        confirm = popDialogUtils.pop_confirm_dialog(self.parent, f'是否将文件：{old_path}\n重命名为：{new_path}')
        if confirm:
            item.setText(0, new_name)
            self.rename_item_signal.emit(old_path, new_path, new_name)
        pass

    def remove_item_file(self, item):
        "删除指定item的文件"
        path = self.get_full_path(item)
        confirm = popDialogUtils.pop_confirm_dialog(self.parent, f'是否删除文件：{path}\n（无法恢复!）')
        if confirm:
            parent = item.parent()
            if parent is None:
                parent = item.treeWidget()
                parent.takeTopLevelItem(parent.indexOfTopLevelItem(item))
            else:
                parent.removeChild(item)
            self.remove_item_signal.emit(path)
        pass

    def traverse(self, func):
        traverse(self, func)
        pass

    def show_extensions_files(self, extensions):
        "显示特定后缀名的文件"
        if extensions is None:
            traverse(self, lambda item: item.setHidden(False))
        else:
            traverse(self, partial(self.select_extensions_files, extensions=extensions))
        pass

    def item_index_of_item(self, item):
        return item_index_of_item(self, item)

    def get_index_item(self, index):
        return get_index_item(self, index)

    def get_full_path(self, item):
        "得到某个item的实际全路径"

        root = self.root
        parents = self.get_parents(item)
        parents = [parent for parent in parents if parent.text(1) == 'folder']  # 只有文件夹才计算进全路径内
        entire_paths = [root] + [parent.text(0) for parent in parents][::-1] + [item.text(0)]
        path = os_path_join(*entire_paths)
        return path

    def get_tag_items(self, tag, recurse=True):
        flag = Qt.MatchContains | Qt.MatchRecursive if recurse else Qt.MatchContains
        items = self.findItems(tag, flag, 1)
        return items

    def mouseDoubleClickEvent(self, e: QtGui.QMouseEvent) -> None:
        current_items = self.currentItem()
        if current_items is None:
            return
        if current_items.text(1) == 'file':
            full_path = self.get_full_path(current_items)
            self.show_item_signal.emit(full_path)
            return
        if current_items.text(1) == 'folder':
            if current_items.isExpanded():
                current_items.setExpanded(False)
            else:
                current_items.setExpanded(True)
        pass

    @staticmethod
    def get_parents(item):
        "得到该item所有的长辈，顺序是从小到大"
        result = []
        parent = item.parent()
        while parent is not None:
            result.append(parent)
            parent = parent.parent()
        return result

    @staticmethod
    def select_extensions_files(item: QTreeWidgetItem, extensions):
        suffix = Path(item.text(0)).suffix
        item.setHidden(True)  # 先什么都不管，隐藏所有
        if item.text(1) == 'file' and suffix in extensions:
            # 只有符合条件的文件以及他的长辈们才能显示
            item.setHidden(False)
            for i in TreeWidget.get_parents(item):
                i.setHidden(False)

    @staticmethod
    def select_special_items(item: QTreeWidgetItem, special_items):
        item.setHidden(True)
        if item in special_items:
            item.setHidden(False)
            for i in TreeWidget.get_parents(item):
                i.setHidden(False)
        pass

    @staticmethod
    def get_leaf_items(items):
        # 得到所有传入的item包含的child，且经过去重
        if not isinstance(items, list):
            items = [items]
        leaf_items = []
        for item in items:
            leaf_items.extend(TreeWidget._get_leaf_items(item))
        # TODO 这里是极低效率的去重
        tmp_leaf_items = []
        [tmp_leaf_items.append(i) for i in leaf_items if not i in tmp_leaf_items]
        leaf_items = tmp_leaf_items
        return leaf_items

    @staticmethod
    def _get_leaf_items(item):
        # 得到一个item包含的child
        leaf_items = []
        if item.text(1) == 'file':
            leaf_items.append(item)
        else:
            for i in range(item.childCount()):
                leaf_items.extend(TreeWidget._get_leaf_items(item.child(i)))
        return leaf_items
