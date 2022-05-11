# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'new_cls_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_NewClsDialog(object):
    def setupUi(self, NewClsDialog):
        NewClsDialog.setObjectName("NewClsDialog")
        NewClsDialog.resize(336, 130)
        NewClsDialog.setMinimumSize(QtCore.QSize(336, 130))
        NewClsDialog.setMaximumSize(QtCore.QSize(336, 133))
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(NewClsDialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(NewClsDialog)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.lineEdit = QtWidgets.QLineEdit(NewClsDialog)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout_2.addWidget(self.lineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_2 = QtWidgets.QLabel(NewClsDialog)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.REdit = QtWidgets.QLineEdit(NewClsDialog)
        self.REdit.setObjectName("REdit")
        self.horizontalLayout.addWidget(self.REdit)
        self.horizontalLayout_5.addLayout(self.horizontalLayout)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtWidgets.QLabel(NewClsDialog)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.GEdit = QtWidgets.QLineEdit(NewClsDialog)
        self.GEdit.setObjectName("GEdit")
        self.horizontalLayout_3.addWidget(self.GEdit)
        self.horizontalLayout_5.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_4 = QtWidgets.QLabel(NewClsDialog)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_4.addWidget(self.label_4)
        self.BEdit = QtWidgets.QLineEdit(NewClsDialog)
        self.BEdit.setObjectName("BEdit")
        self.horizontalLayout_4.addWidget(self.BEdit)
        self.horizontalLayout_5.addLayout(self.horizontalLayout_4)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem)
        self.okButton = QtWidgets.QPushButton(NewClsDialog)
        self.okButton.setObjectName("okButton")
        self.horizontalLayout_6.addWidget(self.okButton)
        self.cancelButton = QtWidgets.QPushButton(NewClsDialog)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout_6.addWidget(self.cancelButton)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(NewClsDialog)
        QtCore.QMetaObject.connectSlotsByName(NewClsDialog)

    def retranslateUi(self, NewClsDialog):
        _translate = QtCore.QCoreApplication.translate
        NewClsDialog.setWindowTitle(_translate("NewClsDialog", "Dialog"))
        self.label.setText(_translate("NewClsDialog", "类别名称"))
        self.label_2.setText(_translate("NewClsDialog", "R"))
        self.label_3.setText(_translate("NewClsDialog", "G"))
        self.label_4.setText(_translate("NewClsDialog", "B"))
        self.okButton.setText(_translate("NewClsDialog", "OK"))
        self.cancelButton.setText(_translate("NewClsDialog", "Cancel"))
