# encoding: utf-8
"""
@author: Soshio
@file: listWidgetItem.py
@time:  下午1:56
@desc:
"""
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QGraphicsSceneMouseEvent, \
    QGraphicsSceneDragDropEvent, QGraphicsSceneHoverEvent, QGraphicsSceneWheelEvent, \
    QGraphicsObject, QListWidgetItem
from ui import res


class ListWidgetItem(QListWidgetItem):
    def __init__(self, text):
        super(ListWidgetItem, self).__init__(text)
        self.color = QColor()

    def set_color(self, color: QColor):
        self.color = color

    @classmethod
    def create_item(cls, text, color):
        item = cls(text)
        item.set_color(color)
        img = QImage(':/icons/颜色圆.svg')
        for h in range(img.width()):
            for l in range(img.height()):
                if img.pixelColor(h, l).green() != 255:
                    img.setPixelColor(h, l, color)
        item.setIcon(QIcon(QPixmap(img)))
        return item
