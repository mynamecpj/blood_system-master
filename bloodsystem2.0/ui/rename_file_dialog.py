# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'rename_file_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_renamefileDialog(object):
    def setupUi(self, renamefileDialog):
        renamefileDialog.setObjectName("renamefileDialog")
        renamefileDialog.resize(226, 121)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(renamefileDialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.label = QtWidgets.QLabel(renamefileDialog)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.lineEdit = QtWidgets.QLineEdit(renamefileDialog)
        self.lineEdit.setObjectName("lineEdit")
        self.verticalLayout.addWidget(self.lineEdit)
        self.buttonBox = QtWidgets.QDialogButtonBox(renamefileDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(renamefileDialog)
        self.buttonBox.accepted.connect(renamefileDialog.accept)
        self.buttonBox.rejected.connect(renamefileDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(renamefileDialog)

    def retranslateUi(self, renamefileDialog):
        _translate = QtCore.QCoreApplication.translate
        renamefileDialog.setWindowTitle(_translate("renamefileDialog", "重命名"))
        self.label.setText(_translate("renamefileDialog", "请输入新名称："))
