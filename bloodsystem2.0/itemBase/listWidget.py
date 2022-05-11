# encoding: utf-8
"""
@author: red0orange
@file: listWidget.py
@time:  下午6:49
@desc:
"""
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QMenu, QAction
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QImage, QIcon, QPixmap, QCursor

from itemBase.listWidgetItem import ListWidgetItem
from utils import popDialogUtils


class ListWidget(QListWidget):
    append_item_signal = pyqtSignal(str, tuple, int)
    rename_item_signal = pyqtSignal(str, str)
    delete_item_signal = pyqtSignal(str)

    def __init__(self, parent):
        super(ListWidget, self).__init__(parent)
        self.parent = self.parentWidget()

        # TODO 把controlUi做成utils的形式，但是弹窗的parent还没解决
        self.menu = QMenu()
        self.append_action = QAction('增加类别', self.parent)
        self.rename_action = QAction('重命名该类别', self.parent)
        self.delete_action = QAction('删除该类别', self.parent)
        self.menu.addAction(self.append_action)
        self.menu.addAction(self.rename_action)
        self.menu.addAction(self.delete_action)

        self.setContextMenuPolicy(Qt.CustomContextMenu)

        self.customContextMenuRequested.connect(self.show_list_widget_menu)
        pass

    def show_list_widget_menu(self, point):
        "分发menu的多个选项的事件"
        current_items = self.selectedItems()
        current_action = self.menu.exec(QCursor.pos())
        if current_action is None:
            return
        if current_action == self.rename_action:
            self.menu_rename_slot(current_items)
        elif current_action == self.append_action:
            self.menu_append_slot(current_items)
        elif current_action == self.delete_action:
            self.menu_delete_slot(current_items)
        pass

    def menu_rename_slot(self, current_items):
        "接收菜单的重命名的事件"
        if len(current_items) != 1:
            popDialogUtils.pop_warning_dialog(self.parent, '无法同时重命名多个类别')
        current_item = current_items[0]
        old_name = current_item.text()
        new_name = popDialogUtils.pop_text_dialog(self.parent, current_item.text())
        if new_name is not None:
            current_item.setText(new_name)
            self.rename_item_signal.emit(old_name, new_name)
        pass

    def menu_append_slot(self, current_items):
        "接收菜单的增加类别的事件"
        if len(current_items) == 0:
            # 应对class list为空的情况
            row = 0
        else:
            if len(current_items) != 1:
                popDialogUtils.pop_warning_dialog(self.parent, '请勿同时选择多个类别')
            current_item = current_items[0]
            row = self.row(current_item)
        class_name, RGB = popDialogUtils.pop_color_dialog(self.parent)
        if class_name is not None and RGB is not None:
            class_name = class_name.strip()
            if len(self.findItems(class_name, Qt.MatchExactly)) == 0:
                # TODO 使这个ListWidget更具有普适性
                item = ListWidgetItem.create_item(class_name, QColor(RGB[0], RGB[1], RGB[2]))
                self.add_item(item, row + 1)
                self.append_item_signal.emit(class_name, RGB, row + 1)
        pass

    def menu_delete_slot(self, current_items):
        "接收菜单的删除类别的事件"
        for current_item in current_items:
            self.delete_item(current_item)
            self.delete_item_signal.emit(current_item.text())
        pass

    def delete_item(self, any):
        "仅仅只是包装一个删除函数备用"
        if isinstance(any, QListWidgetItem):
            row = self.row(any)
            self.takeItem(row)
            self.update()
        elif isinstance(any, int):
            self.takeItem(any)
            self.update()
        else:
            raise BaseException('delete list widget item error')

    def add_item(self, item, p0=None):
        "仅仅只是包装一个增加函数备用"
        if p0 is None:
            self.addItem(item)
        else:
            try:
                self.insertItem(p0, item)
            except:
                raise BaseException('添加listWidgetItem的插入位置错误')

    def get_current_item_text(self):
        return self.currentItem().text()

    def set_current_item(self, any):
        if isinstance(any, QListWidgetItem):
            self.setCurrentItem(any)
        elif isinstance(any, int):
            self.setCurrentRow(any)
        else:
            raise BaseException('输入类型错误')
