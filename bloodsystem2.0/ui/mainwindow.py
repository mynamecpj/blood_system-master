# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1545, 808)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setMinimumSize(QtCore.QSize(100, 30))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.horizontalLayout_4.addWidget(self.comboBox)
        self.fresh_button = QtWidgets.QPushButton(self.centralwidget)
        self.fresh_button.setObjectName("fresh_button")
        self.horizontalLayout_4.addWidget(self.fresh_button)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.image_path_label = QtWidgets.QLabel(self.centralwidget)
        self.image_path_label.setObjectName("image_path_label")
        self.horizontalLayout_4.addWidget(self.image_path_label)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.camera_label = QtWidgets.QLabel(self.centralwidget)
        self.camera_label.setObjectName("camera_label")
        self.horizontalLayout_4.addWidget(self.camera_label)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem2)
        self.pushButton_stop = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_stop.setMinimumSize(QtCore.QSize(150, 30))
        self.pushButton_stop.setObjectName("pushButton_stop")
        self.horizontalLayout_4.addWidget(self.pushButton_stop)
        self.detect_button = QtWidgets.QPushButton(self.centralwidget)
        self.detect_button.setMinimumSize(QtCore.QSize(150, 30))
        self.detect_button.setObjectName("detect_button")
        self.horizontalLayout_4.addWidget(self.detect_button)
        self.verticalLayout_5.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.fileTreeTabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.fileTreeTabWidget.setMaximumSize(QtCore.QSize(500, 16777215))
        font = QtGui.QFont()
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.fileTreeTabWidget.setFont(font)
        self.fileTreeTabWidget.setTabletTracking(False)
        self.fileTreeTabWidget.setAcceptDrops(False)
        self.fileTreeTabWidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.fileTreeTabWidget.setAutoFillBackground(False)
        self.fileTreeTabWidget.setTabPosition(QtWidgets.QTabWidget.West)
        self.fileTreeTabWidget.setObjectName("fileTreeTabWidget")
        self.file = QtWidgets.QWidget()
        self.file.setObjectName("file")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.file)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.fileTreeWidget = FileTreeWidget(self.file)
        self.fileTreeWidget.setMaximumSize(QtCore.QSize(600, 16777215))
        self.fileTreeWidget.setObjectName("fileTreeWidget")
        self.verticalLayout_2.addWidget(self.fileTreeWidget)
        self.fileTreeTabWidget.addTab(self.file, "")
        self.find = QtWidgets.QWidget()
        self.find.setObjectName("find")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.find)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.find_file_line_edit = QtWidgets.QLineEdit(self.find)
        self.find_file_line_edit.setMinimumSize(QtCore.QSize(50, 0))
        self.find_file_line_edit.setObjectName("find_file_line_edit")
        self.horizontalLayout_2.addWidget(self.find_file_line_edit)
        self.find_file_enter_button = QtWidgets.QPushButton(self.find)
        self.find_file_enter_button.setMaximumSize(QtCore.QSize(70, 16777215))
        self.find_file_enter_button.setIconSize(QtCore.QSize(20, 20))
        self.find_file_enter_button.setObjectName("find_file_enter_button")
        self.horizontalLayout_2.addWidget(self.find_file_enter_button)
        self.horizontalLayout_2.setStretch(0, 3)
        self.horizontalLayout_2.setStretch(1, 1)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.findTreeWidget = FindTreeWidget(self.find)
        self.findTreeWidget.setObjectName("findTreeWidget")
        self.verticalLayout.addWidget(self.findTreeWidget)
        self.verticalLayout_3.addLayout(self.verticalLayout)
        self.fileTreeTabWidget.addTab(self.find, "")
        self.star = QtWidgets.QWidget()
        self.star.setObjectName("star")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.star)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.starTreeWidget = StarTreeWidget(self.star)
        self.starTreeWidget.setObjectName("starTreeWidget")
        self.verticalLayout_4.addWidget(self.starTreeWidget)
        self.fileTreeTabWidget.addTab(self.star, "")
        self.show = QtWidgets.QWidget()
        self.show.setObjectName("show")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.show)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout()
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.last_label = QtWidgets.QLabel(self.show)
        self.last_label.setMinimumSize(QtCore.QSize(0, 0))
        self.last_label.setObjectName("last_label")
        self.verticalLayout_7.addWidget(self.last_label)
        self.graphicsView_current = GraphicsView(self.show)
        self.graphicsView_current.setObjectName("graphicsView_current")
        self.verticalLayout_7.addWidget(self.graphicsView_current)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem3)
        self.whole_label = QtWidgets.QLabel(self.show)
        self.whole_label.setObjectName("whole_label")
        self.horizontalLayout_7.addWidget(self.whole_label)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem4)
        self.verticalLayout_7.addLayout(self.horizontalLayout_7)
        self.graphicsView_whole = GraphicsView(self.show)
        self.graphicsView_whole.setObjectName("graphicsView_whole")
        self.verticalLayout_7.addWidget(self.graphicsView_whole)
        self.horizontalLayout_6.addLayout(self.verticalLayout_7)
        self.fileTreeTabWidget.addTab(self.show, "")
        self.horizontalLayout_3.addWidget(self.fileTreeTabWidget)
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout_3.addWidget(self.line)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pre_button = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pre_button.sizePolicy().hasHeightForWidth())
        self.pre_button.setSizePolicy(sizePolicy)
        self.pre_button.setMinimumSize(QtCore.QSize(25, 200))
        self.pre_button.setMaximumSize(QtCore.QSize(30, 500))
        self.pre_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pre_button.setObjectName("pre_button")
        self.horizontalLayout.addWidget(self.pre_button)
        self.graphicsView = GraphicsView(self.centralwidget)
        self.graphicsView.setMinimumSize(QtCore.QSize(960, 640))
        self.graphicsView.setMaximumSize(QtCore.QSize(30000, 30000))
        self.graphicsView.setObjectName("graphicsView")
        self.horizontalLayout.addWidget(self.graphicsView)
        self.next_button = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.next_button.sizePolicy().hasHeightForWidth())
        self.next_button.setSizePolicy(sizePolicy)
        self.next_button.setMinimumSize(QtCore.QSize(25, 200))
        self.next_button.setMaximumSize(QtCore.QSize(30, 500))
        self.next_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.next_button.setStyleSheet("")
        self.next_button.setObjectName("next_button")
        self.horizontalLayout.addWidget(self.next_button)
        self.horizontalLayout_3.addLayout(self.horizontalLayout)
        self.nameList = ListWidget(self.centralwidget)
        self.nameList.setMinimumSize(QtCore.QSize(150, 500))
        self.nameList.setMaximumSize(QtCore.QSize(200, 16777215))
        self.nameList.setObjectName("nameList")
        self.horizontalLayout_3.addWidget(self.nameList)
        self.verticalLayout_5.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_current_save = QtWidgets.QLabel(self.centralwidget)
        self.label_current_save.setObjectName("label_current_save")
        self.horizontalLayout_5.addWidget(self.label_current_save)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem5)
        self.pushButton_start_end = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_start_end.setMinimumSize(QtCore.QSize(200, 40))
        self.pushButton_start_end.setObjectName("pushButton_start_end")
        self.horizontalLayout_5.addWidget(self.pushButton_start_end)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem6)
        self.label_cell_sum = QtWidgets.QLabel(self.centralwidget)
        self.label_cell_sum.setObjectName("label_cell_sum")
        self.horizontalLayout_5.addWidget(self.label_cell_sum)
        self.verticalLayout_5.addLayout(self.horizontalLayout_5)
        self.gridLayout.addLayout(self.verticalLayout_5, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1545, 26))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        self.tools = QtWidgets.QMenu(self.menubar)
        self.tools.setObjectName("tools")
        MainWindow.setMenuBar(self.menubar)
        self.root_directory_act = QtWidgets.QAction(MainWindow)
        self.root_directory_act.setObjectName("root_directory_act")
        self.generate_repoter_act = QtWidgets.QAction(MainWindow)
        self.generate_repoter_act.setCheckable(False)
        self.generate_repoter_act.setObjectName("generate_repoter_act")
        self.export_cutting_act = QtWidgets.QAction(MainWindow)
        self.export_cutting_act.setObjectName("export_cutting_act")
        self.open_dir_action = QtWidgets.QAction(MainWindow)
        self.open_dir_action.setObjectName("open_dir_action")
        self.back_to_start_act = QtWidgets.QAction(MainWindow)
        self.back_to_start_act.setObjectName("back_to_start_act")
        self.import_star_action = QtWidgets.QAction(MainWindow)
        self.import_star_action.setObjectName("import_star_action")
        self.export_star_action = QtWidgets.QAction(MainWindow)
        self.export_star_action.setObjectName("export_star_action")
        self.observe_mode_action = QtWidgets.QAction(MainWindow)
        self.observe_mode_action.setCheckable(True)
        self.observe_mode_action.setObjectName("observe_mode_action")
        self.open_img_action = QtWidgets.QAction(MainWindow)
        self.open_img_action.setObjectName("open_img_action")
        self.create_new_patient_act = QtWidgets.QAction(MainWindow)
        self.create_new_patient_act.setObjectName("create_new_patient_act")
        self.set_save_file_act = QtWidgets.QAction(MainWindow)
        self.set_save_file_act.setObjectName("set_save_file_act")
        self.whole_map_action = QtWidgets.QAction(MainWindow)
        self.whole_map_action.setCheckable(True)
        self.whole_map_action.setChecked(False)
        self.whole_map_action.setObjectName("whole_map_action")
        self.real_time_recheck_action = QtWidgets.QAction(MainWindow)
        self.real_time_recheck_action.setCheckable(True)
        self.real_time_recheck_action.setChecked(False)
        self.real_time_recheck_action.setObjectName("real_time_recheck_action")
        self.camera_setting_action = QtWidgets.QAction(MainWindow)
        self.camera_setting_action.setObjectName("camera_setting_action")
        self.menu.addAction(self.open_img_action)
        self.menu.addAction(self.open_dir_action)
        self.menu.addAction(self.create_new_patient_act)
        self.menu.addSeparator()
        self.menu.addAction(self.set_save_file_act)
        self.menu.addSeparator()
        self.menu.addAction(self.root_directory_act)
        self.menu.addAction(self.back_to_start_act)
        self.menu.addSeparator()
        self.menu.addAction(self.camera_setting_action)
        self.tools.addAction(self.generate_repoter_act)
        self.tools.addSeparator()
        self.tools.addAction(self.export_cutting_act)
        self.tools.addSeparator()
        self.tools.addAction(self.import_star_action)
        self.tools.addAction(self.export_star_action)
        self.tools.addSeparator()
        self.tools.addAction(self.observe_mode_action)
        self.tools.addAction(self.whole_map_action)
        self.tools.addAction(self.real_time_recheck_action)
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.tools.menuAction())

        self.retranslateUi(MainWindow)
        self.fileTreeTabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "血细胞辅助诊断系统"))
        self.comboBox.setItemText(0, _translate("MainWindow", "综合模式"))
        self.comboBox.setItemText(1, _translate("MainWindow", "记录模式"))
        self.fresh_button.setText(_translate("MainWindow", "刷新"))
        self.image_path_label.setText(_translate("MainWindow", "当前显示图片："))
        self.camera_label.setText(_translate("MainWindow", "当前摄像机索引："))
        self.pushButton_stop.setText(_translate("MainWindow", "保存更改"))
        self.detect_button.setText(_translate("MainWindow", "自动标注"))
        self.fileTreeTabWidget.setTabText(self.fileTreeTabWidget.indexOf(self.file), _translate("MainWindow", "所有"))
        self.find_file_enter_button.setText(_translate("MainWindow", "查找"))
        self.fileTreeTabWidget.setTabText(self.fileTreeTabWidget.indexOf(self.find), _translate("MainWindow", "查找"))
        self.fileTreeTabWidget.setTabText(self.fileTreeTabWidget.indexOf(self.star), _translate("MainWindow", "收藏"))
        self.last_label.setText(_translate("MainWindow", "最近一次保存图片："))
        self.whole_label.setText(_translate("MainWindow", "全图"))
        self.fileTreeTabWidget.setTabText(self.fileTreeTabWidget.indexOf(self.show), _translate("MainWindow", "全图与最近保存"))
        self.pre_button.setText(_translate("MainWindow", "<"))
        self.next_button.setText(_translate("MainWindow", ">"))
        self.label_current_save.setText(_translate("MainWindow", "当前保存路径："))
        self.pushButton_start_end.setText(_translate("MainWindow", "开始记录"))
        self.label_cell_sum.setText(_translate("MainWindow", "已标注细胞数量："))
        self.menu.setTitle(_translate("MainWindow", "菜单"))
        self.tools.setTitle(_translate("MainWindow", "工具"))
        self.root_directory_act.setText(_translate("MainWindow", "设置根路径"))
        self.generate_repoter_act.setText(_translate("MainWindow", "生成诊断报告"))
        self.export_cutting_act.setText(_translate("MainWindow", "导出切割图片"))
        self.open_dir_action.setText(_translate("MainWindow", "打开文件夹"))
        self.back_to_start_act.setText(_translate("MainWindow", "恢复初始设置"))
        self.import_star_action.setText(_translate("MainWindow", "导入收藏图片"))
        self.export_star_action.setText(_translate("MainWindow", "导出收藏图片"))
        self.observe_mode_action.setText(_translate("MainWindow", "观察者模式"))
        self.open_img_action.setText(_translate("MainWindow", "打开图片"))
        self.create_new_patient_act.setText(_translate("MainWindow", "新建病人目录"))
        self.set_save_file_act.setText(_translate("MainWindow", "选择病人文件夹"))
        self.whole_map_action.setText(_translate("MainWindow", "全图视图"))
        self.real_time_recheck_action.setText(_translate("MainWindow", "实时查重"))
        self.camera_setting_action.setText(_translate("MainWindow", "相机参数设置"))
from itemBase.fileTreeWidget import FileTreeWidget
from itemBase.findTreeWidget import FindTreeWidget
from itemBase.graphicsView import GraphicsView
from itemBase.listWidget import ListWidget
from itemBase.starTreeWidget import StarTreeWidget
