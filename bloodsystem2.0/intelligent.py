#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2019/11/4 下午9:17
# @Author : red0orange
# @File : intelligent.py
"""
usage: socket的intel接口
"""
from Yolov5Detector import Yolov5Detector
import os
import time
import logging

logger = logging.getLogger("root.intelligent")


class Intelligent:
    def __init__(self):
        model_xml = os.path.join(os.getcwd(), "models/yolov5/yolov5.xml")
        model_bin = os.path.join(os.getcwd(), "models/yolov5/yolov5.bin")
        self.detector = Yolov5Detector(model_xml, model_bin, conf_thres=0.25, iou_thres=0.45)
        pass

    def detect(self, image):
        s = time.perf_counter()
        detect_result = self.detector.detect(image)
        e = time.perf_counter()
        logger.info('time: {}'.format(e - s))
        return detect_result

