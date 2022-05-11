from PyQt5 import QtCore, QtGui, QtWidgets,QtPrintSupport
from PyQt5.QtPrintSupport import QPageSetupDialog,QPrintDialog,QPrinter,QPrintPreviewDialog
from ui.bloodcellcountUI2 import Ui_TEXT
from ui.bloodcellcountUI3 import Ui_MainWindow
from ui.bloodcellcountUI4 import Ui_MainWindow
import sys,os
# import qtawesome
import time
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from threading import Timer
import numpy as np
import threading
from win32 import win32api, win32gui, win32print
from win32.lib import win32con

from win32.win32api import GetSystemMetrics
data=[0.0 for _ in range(50)]

class bloodcellcountUI(Ui_MainWindow, QtWidgets.QMainWindow):#Ui_MainWindow):
     def __init__(self, patientinfo=list):
          super(bloodcellcountUI, self).__init__()
          self.patientinfo= patientinfo
          #打印类继承
          self.printer = QPrinter()
          self.countdata = [0.00 for _ in range(40)]  # 创建40个0的列表
          self.cell_number = np.full((36, 2), 0)  # 构造36x2个列表
          self.cell_percent = np.full((31, 2), 0.00)  # 构造31x2个列表
          #改变报告背景为全白
          self.setStyleSheet("background-color: rgb(255, 255, 255);")
          self.setupUi(self)
          #设置报告名单
          self.setWindowTitle("骨髓细胞学检查图文报告单")
          #设置打印图标
          icon = QtGui.QIcon()
          icon.addPixmap(QtGui.QPixmap("D:/bloodsystem2.0/ui/print.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
          self.action.setIcon(icon)
          #设置报告图标
          self.setWindowIcon(QIcon("D:/bloodsystem2.0/ui/push.png"))
          #对表格进行隐藏操作
          self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)#自适应表格
          self.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
          self.tableWidget.verticalHeader().setVisible(False)#隐藏行标题
          self.tableWidget.horizontalHeader().setVisible(False)#隐藏列标题
          #对表格进行合并单元格操作
          self.tableWidget.setSpan(0,0,2,3)#说明setSpan(row,column,要合并的列数，要合并的行数)
          self.tableWidget.setSpan(2,0,1,3)
          self.tableWidget.setSpan(0,3,1,2)
          self.tableWidget.setSpan(0,5,1,2)
          self.tableWidget.setSpan(3,0,12,1)
          self.tableWidget.setSpan(15,0,7,1)
          self.tableWidget.setSpan(22,0,3,1)
          self.tableWidget.setSpan(25,0,2,1)
          self.tableWidget.setSpan(27,0,2,1)
          self.tableWidget.setSpan(29,0,4,1)
          self.tableWidget.setSpan(33,0,1,7)
          self.tableWidget.setSpan(34,0,1,3)
          self.tableWidget.setSpan(35,1,1,2)
          self.tableWidget.setSpan(36,1,1,2)
          self.tableWidget.setSpan(37,1,1,2)
          self.tableWidget.setSpan(38,1,1,2)
          self.tableWidget.setSpan(39,0,1,3)
          self.tableWidget.setSpan(34,3,1,2)
          self.tableWidget.setSpan(3,1,1,2)
          self.tableWidget.setSpan(4,1,1,2)
          self.tableWidget.setSpan(5,1,4,1)
          self.tableWidget.setSpan(9,1,3,1)
          self.tableWidget.setSpan(12,1,3,1)
          self.tableWidget.setSpan(39,3,1,4)
          for i in range(18):
               self.tableWidget.setSpan(15+i,1,1,2)
          for i in range(6):
               self.tableWidget.setSpan(34+i,5,1,2)
          #设置点击事件
          self.action.triggered.connect(self.open_printer_func)
          self.picture.setToolTip('点击此处插入图片')#设置提示信息
          self.picture.signal_order.connect(self.picture1)
          self.editor = self.splitter
          # 加入储存数据的操作
          self.app_data = QSettings('config.ini', QSettings.IniFormat)
          self.app_data.setIniCodec('UTF-8')
          if os.path.exists('./config.ini'):
               # 如果存在数据就进行初始化
               self.init_info()
          else:
               # 没有数据就认为是第一次打开软件，进行第一次QSettings 数据存储
               self.save_info()
          # 把数据更新到表格中
          self.update_data_thread = UpdateData()
          self.update_data_thread.update_date.connect(self.refresh)  # 链接信号
          self.update_data_thread.start()
          #自动更新病人信息
          self.label_2.setText("科别：血液科")
          self.clinical_diagnosis.setText("临床诊断：")
          self.right_info_lable1.setText("姓名：" + str(self.patientinfo[0]))
          self.right_info_lable2.setText("性别：" + str(self.patientinfo[1]))
          self.right_info_lable3.setText("年龄：" + str(self.patientinfo[2]))
          self.right_info_lable4.setText("检测时间：" + str(self.patientinfo[6]))
          self.right_info_lable5.setText("病床：" + str(self.patientinfo[3]))
          self.label_6.setText("检测日期：" + str(self.patientinfo[6]))
          self.right_info_lable6.setText("采取部位："+str(self.patientinfo[4]))
          self.right_info_lable7.setText("涂片号："+str(self.patientinfo[5]))



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
          #self.tableWidget.setTextElideMode(Qt.AlignHCenter | Qt.AlignVCenter)
          # print(data_rcv)
          for i in range(31):
               all_cell_number_blood = all_cell_number_blood + self.cell_number[i][0]
               all_cell_number_marrow = all_cell_number_marrow + self.cell_number[i][1]
               self.tableWidget.setItem(i + 2, 3, QTableWidgetItem(str(self.cell_number[i][0])))
               self.tableWidget.setItem(i + 2, 5, QTableWidgetItem(str(self.cell_number[i][1])))
          self.tableWidget.setItem(34, 3, QTableWidgetItem(str(all_cell_number_blood) + '   个'))
          self.tableWidget.setItem(34, 5, QTableWidgetItem(str(all_cell_number_marrow) + '   个'))
          for i in range(31, 35):
               self.tableWidget.setItem(i + 4, 3, QTableWidgetItem(str(self.cell_number[i][0]) + '   个'))
               self.tableWidget.setItem(i + 4, 5, QTableWidgetItem(str(self.cell_number[i][1]) + '   个'))
          self.tableWidget.setItem(39, 3, QTableWidgetItem(str(self.cell_number[i][0] + self.cell_number[i][1]) + '   个'))
          for i in range(31):
               # self.model.setItem(i,0,QStandardItem(new_class_name[i]))
               self.tableWidget.setItem(i + 2, 4, QTableWidgetItem(str(self.cell_percent[i][0])))
               self.tableWidget.setItem(i + 2, 6, QTableWidgetItem(str(self.cell_percent[i][1])))
               # self.model.setItem(i,1,QStandardItem(str(data[i])))
               # self.model.setItem(i,2,QStandardItem(unit_name[i]))
               # self.model.setItem(i,3,QStandardItem(range_name[i]))
          # print('refresh over')

     def closeEvent(self, event):
          #self.save_info()
          #设置重写QMessageBox
          self.info = QMessageBox()
          self.info.setIcon(QMessageBox.Information)
          self.info.setWindowTitle('提示')
          self.info.setText("是否要保存报告文本内容?")
          self.info.addButton("保存", QMessageBox.AcceptRole)
          self.info.addButton("不保存", QMessageBox.RejectRole)
          #当没有文本时不会弹窗
          if self.textEdit_2.toPlainText()==""and self.textEdit.toPlainText()==""and self.textEdit_4.toPlainText()=="" and self.clinical_diagnosis_text.text()=="":
               event.accept()

          else:
               self.api = self.info.exec_()
               if self.api == QMessageBox.AcceptRole:
                    #event.accept()
                    self.save_info()
               #sys.exit()  # 退出程序
               else:
                    self.button()
                    #event.accept()
               #sys.exit(0)
          self.update_data_thread.exec()
          #event.accept()



     #输出为pdf
     def open_printer_func(self):
          #self.textEdit_2.setFrameShape("QFrame.Box")
          printer_dialog = QPrintDialog(self.printer)
          if self.screen_scale_rate==1.5:
              self.editor.resize(1150, 1650)
              #self.widget_3.resize(637,1470)
          if self.screen_scale_rate==1.25:
               self.editor.resize(950,1370)
          if self.screen_scale_rate==1.0:
               self.editor.resize(750,1095)
          if self.screen_scale_rate==1.75:
               self.editor.resize(1350,1930)
          if self.screen_scale_rate==2.0:
               self.editor.resize(1500,2200)
          if self.screen_scale_rate==2.25:
               self.editor.resize(1700,2500)
          #self.editor.resize(1100, 1661)
          if printer_dialog.exec_():
               painter = QPainter(self.printer)
               painter.drawPixmap(20,20,self.editor.grab())#把控件变为图片打印

     #保存图片
     def picture1(self):
          self.editor.resize(1100, 1661)
          if self.screen_scale_rate==1.5:
              #self.editor.resize(1150,1650)
              self.picture.resize(500,400)
          if self.screen_scale_rate==1.25:
               self.picture.resize(400,350)
          if self.screen_scale_rate==1.0:
               self.picture.resize(350,300)
          if self.screen_scale_rate==1.75:
               self.picture.resize(550,500)
          if self.screen_scale_rate==2.0:
               self.picture.resize(600,600)
          if self.screen_scale_rate==2.25:
               self.picture.resize(750,700)
          imgName, imgType = QFileDialog.getOpenFileName(self, "打开图片", "", "*.jpg;;*.png;;All Files(*)")
          self.jpg = QtGui.QPixmap(imgName).scaled(self.picture.width(), self.picture.height())
          self.picture.setPixmap(self.jpg)



     #改为A4大小，不用点击也可以，现已删除该功能
     #def tiaozhen(self):
          #self.editor.resize(1081, 1661)
          #self.Widget.resize(1203,1685)

     def get_real_resolution():
          """获取真实的分辨率"""
          hDC = win32gui.GetDC(0)
          # 横向分辨率
          w = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
          # 纵向分辨率
          h = win32print.GetDeviceCaps(hDC, win32con.DESKTOPVERTRES)
          return w, h

     def get_screen_size():
          """获取缩放后的分辨率"""
          w = GetSystemMetrics(0)
          h = GetSystemMetrics(1)
          return w, h

     real_resolution = get_real_resolution()
     screen_size = get_screen_size()
     print(real_resolution)
     print(screen_size)

     screen_scale_rate = round(real_resolution[0] / screen_size[0], 2)
     print(screen_scale_rate)

     def save_info(self):
          #time = QDateTime.currentDateTime()  # 获取当前时间，并存储在self.qpp_data
          #self.app_data.setValue('time', time.toString())  # 数据0：time.toString()为字符串类型
          self.text1=self.textEdit.toPlainText()# 获取当前文本框的内容
          self.text2=self.textEdit_2.toPlainText()#获取文本内容
          self.text3=self.textEdit_4.toPlainText()#获取文本内容
          self.line=self.clinical_diagnosis_text.text()#获取文本框内容
          #self.pic=self.picture.pixmap().toImage()
          #self.app_data.setValue('self.pic',QVariant(self.picture.pixmap()))
          self.app_data.setValue('self.text1', self.text1)# 数据1
          self.app_data.setValue('self.text2', self.text2)
          self.app_data.setValue('self.text3', self.text3)
          self.app_data.setValue('self.line', self.line)
          #self.app_data.setValue('self.pic',QVariant(self.pic))


     def init_info(self):
          self.text1 = self.app_data.value('self.text1')
          self.text2 = self.app_data.value('self.text2')
          self.text3 = self.app_data.value('self.text3')
          self.line = self.app_data.value('self.line')
          #self.pic=self.app_data.value('self.pic')
          self.textEdit.setPlainText(self.text1)
          self.textEdit_2.setPlainText(self.text2)
          self.textEdit_4.setPlainText(self.text3)
          self.clinical_diagnosis_text.setText(self.line)
          #self.picture.setPixmap(self.pic)

     def button(self):
          # 删除QSettings数据
          QSettings.clear(self.app_data)

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


# 自定义label，用于传递是哪个label被点击了，生成UI文件后要复制此段到UI文件最后，修改self.picture继承的类为Mylabel
class MyLabel(QtWidgets.QLabel):
    signal_order = pyqtSignal(int)

    def __init__(self, order=None):
        super(MyLabel, self).__init__()
        self.order = order

    def mousePressEvent(self, e):  # 重载鼠标点击事件
        self.signal_order.emit(self.order)





     #def showSetting(self):
          #dcdd=QPageSetupDialog(self.printer,self)
          #dcdd.exec()



     #def print(self):
          #printdialog = QPrintDialog(self.printer, self)
          #if QDialog.Accepted == printdialog.exec():
               #self.editor.print(self.printer)

















#if __name__ == "__main__":
    #app = QApplication(sys.argv)
    #main = SimpleDialogForm()
    #main.show()#在外面只需要调用simpleDialogForm显示就行，不需要关注内部如何实现了。
    #sys.exit(app.exec_())




