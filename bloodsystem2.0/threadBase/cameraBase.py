# encoding: utf-8
"""
@author: Soshio
@file: cameraBase.py
@time:  下午1:56
@desc:
"""
import numpy as np
import sys
import utils.toupcam as toupcam
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtCore import pyqtSignal, QThread
from utils.popDialogUtils import *

import logging

logger = logging.getLogger("root.cameraBase")

def frame2mat(Buffer, w, h):
    bits = np.uint8 
    mat = np.frombuffer(Buffer, bits)
    mat = mat.reshape(h, w, 3)   #转换维度

    return mat

class ConfigPropertyException(BaseException):
    pass

class CameraThread(QThread):
    imageSignal = pyqtSignal(np.ndarray, int, int)
    cameralabelSignal = pyqtSignal(int, str)
    eventImage = pyqtSignal()

    def __init__(self):
        super(CameraThread, self).__init__()
        self.hcam = None
        self.buf = None      # video buffer
        self.w = 0           # video width
        self.h = 0           # video height
        self.total = 0
        self.camera_inf = []
        # [Hue, Contrast, Saturation, ExpoTime, ExpoAGain, Gamma]

    @staticmethod
    def cameraCallback(nEvent, ctx):
        if nEvent == toupcam.TOUPCAM_EVENT_IMAGE:
            ctx.eventImage.emit()
    
    @pyqtSlot()
    def eventImageSignal(self):
        if self.hcam is not None:
            try:
                self.hcam.PullImageV2(self.buf, 24, None)
                self.total += 1
            except toupcam.HRESULTException as ex:
                QMessageBox.warning(self, '', 'pull image failed, hr=0x{:x}'.format(ex.hr), QMessageBox.Ok)
            else:
                img = frame2mat(self.buf, self.w, self.h)
                self.imageSignal.emit(img, self.w, self.h)

    def check_out(self,):
        self.cameraInfo = toupcam.Toupcam.EnumV2()  # 刷新并获取相机列表
        camera_flag = True
        if (len(self.cameraInfo) == 0):  # 没有任何设备则退出
            pop_warning_dialog(None, "没有找到设备")
            camera_flag = False

        for k, v in enumerate(self.cameraInfo):  # 打印相机索引和名称
            self.cameralabelSignal.emit(k, v.displayname)

        return camera_flag

    def run(self):
        self.eventImage.connect(self.eventImageSignal)
        try:
            self.hcam = toupcam.Toupcam.Open(self.cameraInfo[0].id)
        except toupcam.HRESULTException as ex:
            QMessageBox.warning(self, '', 'failed to open camera, hr=0x{:x}'.format(ex.hr), QMessageBox.Ok)
        else:
            self.w, self.h = self.hcam.get_Size()
            bufsize = ((self.w * 24 + 31) // 32 * 4) * self.h
            self.buf = bytes(bufsize)        
            try:
                if sys.platform == 'win32':
                    self.hcam.put_Option(toupcam.TOUPCAM_OPTION_BYTEORDER, 0) # QImage.Format_RGB888
                    self.hcam.put_Contrast(int(self.camera_inf[1]))
                    self.hcam.put_Saturation(int(self.camera_inf[2]))
                    self.hcam.put_Hue(int(self.camera_inf[0]))
                    self.hcam.put_ExpoTime(int(self.camera_inf[3]))
                    self.hcam.put_ExpoAGain(int(self.camera_inf[4]))
                    self.hcam.put_Gamma(int(self.camera_inf[5]))
                self.hcam.StartPullModeWithCallback(self.cameraCallback, self)
            except toupcam.HRESULTException as ex:
                QMessageBox.warning(self, '', 'failed to start camera, hr=0x{:x}'.format(ex.hr), QMessageBox.Ok)


    def exit_thread(self):
        if self.hcam is not None:
            self.hcam.Close()
            self.hcam = None
            