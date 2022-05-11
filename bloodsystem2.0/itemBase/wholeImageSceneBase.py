# encoding: utf-8
"""
@author: Soshio
@file: wholeImageSceneBase.py
@time:  下午1:56
@desc:
"""
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class WholeImageSceneBase(QGraphicsScene):

    def __init__(self, parent):
        self.img = QImage()
        self.img_path = None
        super(WholeImageSceneBase, self).__init__(parent)
        self.parent = parent
        self.Path = QPainterPath()

        self.rect = QRectF(0, 0, 330, 220)
        self.setSceneRect(self.rect)
        self.setParent(self.parent)

    def whole_set_img(self, image_path):
        self.img = QImage(image_path)
        self.img_path = image_path
        self.update()
        pass

    def drawBackground(self, painter: QPainter, rect: QRectF):
        painter.drawImage(self.rect, self.img)
        Pen = QPen(Qt.blue)
        Pen.setWidth(3)
        painter.setPen(Pen)
        painter.drawPath(self.Path)
