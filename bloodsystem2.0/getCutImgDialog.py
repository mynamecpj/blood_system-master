# -*- coding: utf-8 -*-
"""
Created on Sun Jul 19 16:37:29 2020

@author: 石头汤
"""

import sys
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import Qt  # , QFile, pyqtSignal
from ui.getCutImgDialog import Ui_cut_img_dialog
from utils.popDialogUtils import pop_file_dialog


class CutImgDialog(QDialog):

    def __init__(self, file_tree, parent=None):
        super(CutImgDialog, self).__init__(parent)
        self.ui = Ui_cut_img_dialog()
        self.ui.setupUi(self)
        self.parent_tree = file_tree
        self.root_path = file_tree.root
        self.file_tree_init()

        self.result_paths = None

    def file_tree_init(self):
        # 文件树stackWidget的所有槽函数
        self.tree = self.ui.treeWidget
        self.tree.init(self.parent_tree)

        # connect signal
        self.tree.itemChanged.connect(self.related_main)
        self.ui.decide_button_box.accepted.connect(self.get_path)
        self.ui.choose_save_root_button.clicked.connect(self.select_save_root_button_slot)
        pass

    def select_save_root_button_slot(self):
        path = pop_file_dialog(self, 'dir', '请选择保存路径')
        if path is None:
            return
        self.ui.save_root_line_edit.setText(path)
        pass

    def related_main(self, item):
        # 父子节点复选框自动关联实现总函数
        # print(item.text(0))
        if item == None:  # 到达递归底端
            return
        state = item.checkState(0)
        if item.childCount() > 0 and state != 1:
            # 防止PartiallyChecked的时候产生不必要的状态改变造成死循环
            self.check_all_child(item, state)
        self.check_bro_changed(item)

    def check_all_child(self, item, state):
        # 子项全选/全不选
        childCount = item.childCount()
        if childCount == 0:  # 到达递归底端
            return
        if state == Qt.Checked:
            for i in range(childCount):
                child = item.child(i)
                child.setCheckState(0, Qt.Checked)
        else:
            for i in range(childCount):
                child = item.child(i)
                child.setCheckState(0, Qt.Unchecked)
                self.check_all_child(child, state)
        pass

    def check_bro_changed(self, item):
        # 子节点对父节点产生影响
        if item == None:  # 到达递归底端
            return
        siblingState = self.check_sibling(item)
        # print(siblingState)
        parent = item.parent()
        # print(parent)
        if parent == None:  # 到达递归顶端
            return
        if siblingState == Qt.PartiallyChecked:
            if parent.checkState(0) != 1:  # 防止无谓的改变状态造成的死循环，下同
                parent.setCheckState(0, Qt.PartiallyChecked)
        elif siblingState == Qt.Checked:
            if parent.checkState(0) != 2:
                parent.setCheckState(0, Qt.Checked)
        else:
            if parent.checkState(0) != 0:
                parent.setCheckState(0, Qt.Unchecked)
        self.check_bro_changed(parent)

    def check_sibling(self, item):
        # 用以获取兄弟节点的状态以改变父节点状态的函数
        parent = item.parent()  # 获取父节点
        if parent == None:  # 若为当前节点为顶层则直接返回状态
            return item.checkState(0)
        brotherCount = parent.childCount()
        checkedCount = 0
        unCheckedCount = 0
        for i in range(brotherCount):
            brother = parent.child(i)
            state = brother.checkState(0)
            if state == Qt.PartiallyChecked:  # 部分选中
                return Qt.PartiallyChecked
            elif state == Qt.Unchecked:  # 未选中
                unCheckedCount = unCheckedCount + 1
            else:  # 选中
                checkedCount = checkedCount + 1
            if checkedCount > 0 and unCheckedCount > 0:
                return Qt.PartiallyChecked
        if unCheckedCount > 0:
            return Qt.Unchecked
        return Qt.Checked

    def get_path(self):
        # 按确认按钮后返回所有已选中的路径
        items = []

        def get_checked_items(item):
            if item.checkState(0) == Qt.Checked and item.text(1) == 'file':
                items.append(item)

        self.tree.traverse(get_checked_items)
        image_paths = [self.tree.get_full_path(item=i) for i in items]
        self.result_paths = image_paths
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = CutImgDialog()
    print(myWin.exec())
