# encoding: utf-8
"""
@author: Soshio
@file: lastImageSceneBase.py
@time:  下午1:56
@desc:
"""
from PyQt5.QtWidgets import QGraphicsScene,QGraphicsSceneMouseEvent,QGraphicsSceneWheelEvent,QWidget,QGraphicsItem
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from random import choice
from itemBase.itemBase import ItemBase

from utils.utils import *

class LastImageSceneBase(QGraphicsScene):

    def __init__(self, parent):
        self.img = QImage()
        self.img_path = None
        self.xml_path = None
        super(LastImageSceneBase, self).__init__(parent)
        self.parent = parent
        self.Path = QPainterPath()
        self.pathStartPos = None
        self.deleteModel = False

        self.rect = QRectF(0, 0, 330, 220)
        self.setSceneRect(self.rect)
        self.setParent(self.parent)

    def lp_set_img(self, image_path):
        self.img = QImage(image_path)
        self.img_path = image_path
        self.update()
        pass

    def drawBackground(self, painter: QPainter, rect: QRectF):
        painter.drawImage(self.rect,self.img)
        Pen = QPen(Qt.blue)
        Pen.setWidth(3)
        painter.setPen(Pen)
        painter.drawPath(self.Path)
        if self.pathStartPos and self.Path.currentPosition():
            painter.drawLine(self.pathStartPos,self.Path.currentPosition())
        pass

    def add_item(self, items):
        "向scene添加item"
        items = listy(items)
        for i in range(len(items)):
            items[i].lockFlag = True
            self.addItem(items[i])
        self.update()
        pass
