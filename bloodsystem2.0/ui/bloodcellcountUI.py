# encoding: utf-8
"""
@author: Luqinghang, Soshio
@file: recheckBase.py
@time:  下午1:56
@desc:
"""
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
# import qtawesome
import time
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from threading import Timer
import numpy as np
import threading

# class_name = ['P-H畸形','产板巨核细胞','大血小板','单核细胞','分叶粒细胞','杆状粒细胞','戈谢细胞','浆细胞','浆质体','巨晚幼红细胞','巨早幼红细胞','巨中幼红细胞','颗粒巨核细胞','淋巴细胞','裸核型巨核细胞','嗜碱性粒细胞','嗜碱性晚幼粒细胞','嗜碱性中幼粒细胞','嗜酸性粒细胞','嗜酸性晚幼粒细胞','嗜酸性中幼粒细胞','退化细胞','晚幼红细胞','晚幼粒细胞','网状细胞','血小板','血小板聚集','异型淋巴细胞','原始红细胞','原始粒细胞','原幼稚单核细胞','原幼稚浆细胞','原幼稚巨核细胞','原幼稚淋巴细胞','早幼红细胞','早幼粒细胞','中幼红细胞','中幼粒细胞','组织嗜碱细胞']
# new_class_name = ['白细胞计数','中性粒细胞百分比','淋巴细胞百分比','单核细胞百分比','嗜酸性粒细胞百分比','嗜碱性粒细胞百分比','中性粒细胞计数','淋巴细胞计数','单核细胞计数','嗜酸性粒细胞计数','嗜碱性粒细胞计数','红细胞计数','血红蛋白','红细胞压积','平均红细胞体积','平均血红蛋白量','平均血红蛋白浓度','红细胞分布宽度CV','血小板','血小板平均分布宽度']
# unit_name = ['10^9/L','%','%','%','%','%','10^9/L','10^9/L','10^9/L','10^9/L','10^9/L','10^12/L','g/L','%','fL','pg','g/L','%','10^9/L','fL']
# range_name = ['4.00 - 10.0','50.0 - 70.0','20.0 - 40','3.0 - 10.0','0.4 - 8','0 - 1','2.00 - 7.0','0.8 - 4.00','0.12 - 0.8','0.02 - 0.52','0 - 0.06','4.09 - 5.74','120 - 172','38.0 - 50.8','83.9 - 99.1','27.8 - 33.8','320 - 555','0.0 - 14.6','85.0 - 303.0','12.0 - 22.0']
data = [0.0 for _ in range(50)]


# print(data)

class MyModel(QStandardItemModel):
    def __init__(self, row, column):
        QStandardItemModel.__init__(self, row, column)

    def data(self, index, role=None):
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        return QStandardItemModel.data(self, index, role)


class BloodCellStatisticsUI(QMainWindow):
    def __init__(self, patientinfo=list):
        super().__init__()
        self.patientinfo = patientinfo
        self.countdata = [0.00 for _ in range(40)]#创建40个0的列表
        self.cell_number = np.full((36, 2), 0)#构造36x2个列表
        self.cell_percent = np.full((31, 2), 0.00)#构造31x2个列表
        self.init_ui()

    def init_ui(self):
        self.resize(1200, 960)
        self.setMinimumSize(QtCore.QSize(0, 0))
        self.setMaximumSize(QtCore.QSize(1600, 1600))
        #把数据更新到表格中
        self.update_data_thread = UpdateData()
        self.update_data_thread.update_date.connect(self.refresh)  # 链接信号
        self.update_data_thread.start()

        self.main_widget = QtWidgets.QWidget()  # 创建窗口主部件
        self.main_layout = QtWidgets.QGridLayout()  # 创建主部件的网格布局
        self.main_widget.setLayout(self.main_layout)  # 设置窗口主部件布局为网格布局

        self.left_widget = QtWidgets.QWidget()  # 创建左侧部件
        self.left_widget.setObjectName('left_widget')
        self.left_layout = QtWidgets.QGridLayout()  # 创建左侧部件的网格布局层
        self.left_widget.setLayout(self.left_layout)  # 设置左侧部件布局为网格

        self.right_widget = QtWidgets.QWidget()  # 创建右侧部件
        self.right_widget.setObjectName('right_widget')
        self.right_layout = QtWidgets.QGridLayout()
        self.right_widget.setLayout(self.right_layout)  # 设置右侧部件布局为网格

        self.main_layout.addWidget(self.left_widget, 0, 0, 2, 2)  # 左侧部件在第0行第0列，占8行3列
        self.main_layout.addWidget(self.right_widget, 0, 2, 12, 10)  # 右侧部件在第0行第3列，占8行9列
        self.setCentralWidget(self.main_widget)  # 设置窗口主部件

        # self.left_button_1 = QtWidgets.QPushButton(qtawesome.icon('fa.id-card-o',color='white'),"血细胞报告")
        self.left_button_1 = QtWidgets.QPushButton("血细胞报告")
        self.left_button_1.setObjectName('left_button')
        # self.left_button_2 = QtWidgets.QPushButton("拒识别(尚未完成)")
        # self.left_button_2.setObjectName('left_button')
        self.left_layout.addWidget(self.left_button_1, 2, 0, 1, 3)
        # self.left_layout.addWidget(self.left_button_2, 3, 0,1,3)
        self.right_title_label = QtWidgets.QLabel("骨 髓 细 胞 检 查 报 告")
        self.right_title_label.setObjectName('right_title_label')
        self.right_layout.addWidget(self.right_title_label, 0, 0, 1, 9)
        # self.right_layout.addWidget(self.right_title_label)

        self.right_info_widget = QtWidgets.QWidget()  # 患者信息部件
        self.right_info_layout = QtWidgets.QGridLayout()  # 患者信息布局
        self.right_info_widget.setLayout(self.right_info_layout)
        self.right_info_widget.setObjectName('right_info_widget')
        # self.right_layout.addWidget(self.right_recommend_label, 1, 0, 1, 9)
        self.right_info_lable1 = QtWidgets.QLabel("姓名：" + str(self.patientinfo[0]))
        self.right_info_lable2 = QtWidgets.QLabel("性别：" + str(self.patientinfo[1]))
        self.right_info_lable3 = QtWidgets.QLabel("年龄：" + str(self.patientinfo[2]))
        self.right_info_lable4 = QtWidgets.QLabel("检测时间：" + str(self.patientinfo[4]))
        self.right_info_lable5 = QtWidgets.QLabel("病床：" + str(self.patientinfo[3]))
        self.right_info_layout.addWidget(self.right_info_lable1, 0, 0)
        self.right_info_layout.addWidget(self.right_info_lable2, 0, 1)
        self.right_info_layout.addWidget(self.right_info_lable3, 0, 2)
        self.right_info_layout.addWidget(self.right_info_lable4, 1, 0)
        self.right_info_layout.addWidget(self.right_info_lable5, 0, 3)

        self.right_layout.addWidget(self.right_info_widget, 1, 0, 1, 9)

        # 设置数据层次结构，40行7列
        self.model = MyModel(40, 7)
        # self.model=QStandardItemModel(40,7)
        # 设置水平方向四个头标签文本内容
        self.model.setHorizontalHeaderLabels(['类别', '检验项目', '测定结果', '单位', '参考范围'])
        for row in range(40):
            for column in range(7):
                item = QStandardItem('row %s,column %s' % (row, column))
                # 设置每个位置的文本值
                self.model.setItem(row, column, item)

        # 实例化表格视图，设置模型为自定义的模型
        self.tableView = QTableView()
        self.tableView.setModel(self.model)
        self.tableView.setObjectName('table_view')
        self.right_layout.addWidget(self.tableView, 3, 0, 10, 9)
        # 水平方向标签拓展剩下的窗口部分，填满表格
        self.tableView.horizontalHeader().setStretchLastSection(True)
        # 水平方向，表格大小拓展到适当的尺寸
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableView.setStyleSheet("item{border:1px}")

        self.tableView.setSpan(0, 0, 2, 3)  # 设置单元格合并
        self.model.setItem(0, 0, QStandardItem('细 胞 名 称'))
        self.tableView.setSpan(0, 3, 1, 2)  # 设置单元格合并
        self.model.setItem(0, 3, QStandardItem('血  片'))
        self.tableView.setSpan(0, 5, 1, 2)  # 设置单元格合并
        self.model.setItem(0, 5, QStandardItem('髓  片'))
        self.model.setItem(1, 3, QStandardItem('数  量/个'))
        self.model.setItem(1, 4, QStandardItem('百分数/%'))
        self.model.setItem(1, 5, QStandardItem('数  量/个'))
        self.model.setItem(1, 6, QStandardItem('百分数/%'))

        self.tableView.setSpan(2, 0, 1, 3)  # 设置单元格合并
        self.model.setItem(2, 0, QStandardItem('原 始 血 细 胞'))

        self.tableView.setSpan(3, 0, 12, 1)  # 设置单元格合并
        self.model.setItem(3, 0, QStandardItem('粒细胞系统'))
        self.tableView.setSpan(3, 1, 1, 2)  # 设置单元格合并
        self.model.setItem(3, 1, QStandardItem('原 始 粒 细 胞'))
        self.tableView.setSpan(4, 1, 1, 2)  # 设置单元格合并
        self.model.setItem(4, 1, QStandardItem('早 幼 粒 细 胞'))
        self.tableView.setSpan(5, 1, 4, 1)  # 设置单元格合并
        self.model.setItem(5, 1, QStandardItem('中性粒细胞'))
        self.tableView.setSpan(9, 1, 3, 1)  # 设置单元格合并
        self.model.setItem(9, 1, QStandardItem('嗜酸粒细胞'))
        self.tableView.setSpan(12, 1, 3, 1)  # 设置单元格合并
        self.model.setItem(12, 1, QStandardItem('嗜碱粒细胞'))
        self.lixibaoname = ['中    幼', '晚    幼', '杆 状 核', '分 叶 核', '中    幼', '晚    幼', '成    熟', '中    幼', '晚    幼',
                            '成    熟']
        for i in range(len(self.lixibaoname)):
            self.model.setItem(5 + i, 2, QStandardItem(self.lixibaoname[i]))

        self.tableView.setSpan(15, 0, 7, 1)  # 设置单元格合并
        self.model.setItem(15, 0, QStandardItem('红细胞系统'))
        self.hongxibaoname = ['原 始 红 细 胞', '早 幼 红 细 胞', '中 幼 红 细 胞', '晚 幼 红 细 胞', '巨 早 幼 红 细 胞', '巨 中 幼 红 细 胞',
                              '巨 晚 幼 红 细 胞']
        for i in range(len(self.hongxibaoname)):
            self.tableView.setSpan(15 + i, 1, 1, 2)  # 设置单元格合并
            self.model.setItem(15 + i, 1, QStandardItem(self.hongxibaoname[i]))

        self.tableView.setSpan(22, 0, 3, 1)  # 设置单元格合并
        self.model.setItem(22, 0, QStandardItem('淋巴细胞系统'))
        self.linbaxibaoname = ['原幼稚淋巴细胞', '淋  巴  细  胞', '异型淋巴细胞']
        for i in range(len(self.linbaxibaoname)):
            self.tableView.setSpan(22 + i, 1, 1, 2)  # 设置单元格合并
            self.model.setItem(22 + i, 1, QStandardItem(self.linbaxibaoname[i]))

        self.tableView.setSpan(25, 0, 2, 1)  # 设置单元格合并
        self.model.setItem(25, 0, QStandardItem('单核细胞系统'))
        self.danhexibaoname = ['原幼稚单核细胞', '单  核  细  胞']
        for i in range(len(self.danhexibaoname)):
            self.tableView.setSpan(25 + i, 1, 1, 2)  # 设置单元格合并
            self.model.setItem(25 + i, 1, QStandardItem(self.danhexibaoname[i]))

        self.tableView.setSpan(27, 0, 2, 1)  # 设置单元格合并
        self.model.setItem(27, 0, QStandardItem('浆细胞系统'))
        self.jiangxibaoname = ['原幼稚浆细胞', '浆   细   胞']
        for i in range(len(self.jiangxibaoname)):
            self.tableView.setSpan(27 + i, 1, 1, 2)  # 设置单元格合并
            self.model.setItem(27 + i, 1, QStandardItem(self.jiangxibaoname[i]))

        self.tableView.setSpan(29, 0, 4, 1)  # 设置单元格合并
        self.model.setItem(29, 0, QStandardItem('其他细胞'))
        self.qitaxibaoname = ['网  状  细  胞', '内  皮  细  胞', '组织嗜碱细胞', '分类不明细胞']
        for i in range(len(self.qitaxibaoname)):
            self.tableView.setSpan(29 + i, 1, 1, 2)  # 设置单元格合并
            self.model.setItem(29 + i, 1, QStandardItem(self.qitaxibaoname[i]))

        self.tableView.setSpan(33, 0, 1, 7)  # 设置单元格合并
        self.model.setItem(33, 0, QStandardItem('  '))

        self.tableView.setSpan(34, 0, 1, 3)  # 设置单元格合并
        self.model.setItem(34, 0, QStandardItem('细 胞 总 数'))
        self.tableView.setSpan(34, 3, 1, 2)  # 设置单元格合并
        self.model.setItem(34, 3, QStandardItem(''))
        self.tableView.setSpan(34, 5, 1, 2)  # 设置单元格合并
        self.model.setItem(34, 5, QStandardItem(''))

        self.tableView.setSpan(35, 0, 4, 1)  # 设置单元格合并
        self.model.setItem(35, 0, QStandardItem(''))
        self.juhexibaoname = ['原幼稚巨核细胞', '颗粒型巨核细胞', '产板型巨核细胞', '裸核型巨核细胞']
        for i in range(len(self.juhexibaoname)):
            self.tableView.setSpan(35 + i, 1, 1, 2)  # 设置单元格合并
            self.model.setItem(35 + i, 1, QStandardItem(self.juhexibaoname[i]))
            self.tableView.setSpan(35 + i, 3, 1, 2)  # 设置单元格合并
            self.model.setItem(35 + i, 3, QStandardItem(''))
            self.tableView.setSpan(35 + i, 5, 1, 2)  # 设置单元格合并
            self.model.setItem(35 + i, 5, QStandardItem(''))
        self.tableView.setSpan(39, 0, 1, 3)  # 设置单元格合并
        self.model.setItem(39, 0, QStandardItem('退 化 细 胞'))
        self.tableView.setSpan(39, 3, 1, 4)  # 设置单元格合并
        self.model.setItem(39, 3, QStandardItem(''))
        # self.tableView.setSpan(39, 5, 1, 2)#设置单元格合并
        # self.model.setItem(39,5,QStandardItem(''))

        self.tableView.verticalHeader().setVisible(False)
        # self.tableView.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tableView.horizontalHeader().setVisible(False)

        self.right_widget.setStyleSheet('''
            QWidget#right_widget{
                color:#232C51;
                background:white;
                border:1px solid darkGray;
                border-radius:10px;
            }
            QWidget#right_info_widget{
                border:1px solid darkGray;
            }
            QWidget#table_view{
                text-align:center;
                border:1px solid darkGray;
            }
            QLabel#right_lable{
                border:none;
                font-size:16px;
                font-weight:700;
                font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
            }
            QLabel#right_title_label{
                background:#ffffff;
                border-top:2px solid darkGray;
                border-bottom:2px solid darkGray;
                font-size:40px;
                font-weight:600;
                font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
                padding-left:270px;
                padding-top:10px;
                padding-bottom:10px;
                padding-right:10px;
                text-align:center;
            }
        ''')
        self.left_widget.setStyleSheet('''
            QPushButton{border:none;color:black;}
            QPushButton#left_label{
                border:none;
                border-bottom:1px solid white;
                font-size:18px;
                font-weight:700;
                font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
            }
            QPushButton#left_button:hover{border-left:4px solid red;font-weight:700;}
        ''')

    def update_countdata(self, cell_number, cell_percent):
        self.cell_number = cell_number
        self.cell_percent = np.around(cell_percent, 2)

    def update_patient_info(self, p_info):
        self.patientinfo = p_info

    def refresh(self, data_rcv):
        # for i in range(38):
        #     data[i] = data[i] + 1
        all_cell_number_blood = 0
        all_cell_number_marrow = 0
        # print(data_rcv)
        for i in range(31):
            all_cell_number_blood = all_cell_number_blood + self.cell_number[i][0]
            all_cell_number_marrow = all_cell_number_marrow + self.cell_number[i][1]
            self.model.setItem(i + 2, 3, QStandardItem(str(self.cell_number[i][0])))
            self.model.setItem(i + 2, 5, QStandardItem(str(self.cell_number[i][1])))
        self.model.setItem(34, 3, QStandardItem(str(all_cell_number_blood) + '   个'))
        self.model.setItem(34, 5, QStandardItem(str(all_cell_number_marrow) + '   个'))
        for i in range(31, 35):
            self.model.setItem(i + 4, 3, QStandardItem(str(self.cell_number[i][0]) + '   个'))
            self.model.setItem(i + 4, 5, QStandardItem(str(self.cell_number[i][1]) + '   个'))
        self.model.setItem(39, 3, QStandardItem(str(self.cell_number[i][0] + self.cell_number[i][1]) + '   个'))
        for i in range(31):
            # self.model.setItem(i,0,QStandardItem(new_class_name[i]))
            self.model.setItem(i + 2, 4, QStandardItem(str(self.cell_percent[i][0])))
            self.model.setItem(i + 2, 6, QStandardItem(str(self.cell_percent[i][1])))
            # self.model.setItem(i,1,QStandardItem(str(data[i])))
            # self.model.setItem(i,2,QStandardItem(unit_name[i]))
            # self.model.setItem(i,3,QStandardItem(range_name[i]))
        # print('refresh over')

    def closeEvent(self, event):
        self.update_data_thread.exec()
        event.accept()


class UpdateData(QThread):
    """更新数据类"""
    update_date = pyqtSignal(str)

    def __init__(self):
        super(UpdateData, self).__init__()

    def run(self):
        cnt = 0
        while True:
            cnt += 1
            # print(repr(threading.currentThread()))
            # print(cnt)
            # print(self.stop)
            self.update_date.emit(str(cnt))  # 发射信号
            time.sleep(0.2)
