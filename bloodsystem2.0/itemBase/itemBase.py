# encoding: utf-8
"""
@author: Soshio
@file: itemBase.py
@time:  下午1:56
@desc:
"""
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QGraphicsSceneMouseEvent, \
    QGraphicsSceneDragDropEvent, QGraphicsSceneHoverEvent, QGraphicsSceneWheelEvent, \
    QGraphicsObject
from ui import res

from PyQt5 import QtGui


class ItemBase(QGraphicsObject):
    itemSelectedSignal = pyqtSignal()

    def __init__(self, size):
        super(ItemBase, self).__init__()
        self.font = QtGui.QFont()
        self.font.setFamily("Arial") #括号里可以设置成自己想要的其它字体
        self.font.setPointSize(18)
        self._size = size
        self._Pen = QPen(QColor(Qt.black))
        self._drawPath = QPainterPath()
        self._rectPath = QPainterPath()
        self._selectedFlag = 0
        self._Sensitivity = 10
        self._lockFlag = False
        self._categories_id = None
        self._text = ''
        self._probility = {}
        self._cursorFlag = -1  # item.cursor()好像有问题
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.setAcceptHoverEvents(True)

    @property
    def Sensitivity(self):
        return self._Sensitivity

    @Sensitivity.setter
    def Sensitivity(self, value):
        self._Sensitivity = value

    @property
    def cursorFlag(self):
        return self._cursorFlag

    @cursorFlag.setter
    def cursorFlag(self, value):
        self._cursorFlag = value

    @property
    def lockFlag(self):
        return self._lockFlag

    @lockFlag.setter
    def lockFlag(self, value):
        self._lockFlag = value

    @property
    def selectedFlag(self):
        return self._selectedFlag

    @selectedFlag.setter
    def selectedFlag(self, value):
        self._selectedFlag = value

    @property
    def pen(self):
        return self._Pen

    @pen.setter
    def pen(self, value):
        self._Pen = value

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = list(value)

    @property
    def width(self):
        return self.size[0]

    @width.setter
    def width(self, value):
        self.size[0] = value

    @property
    def height(self):
        return self.size[1]

    @height.setter
    def height(self, value):
        self.size[1] = value

    @property
    def categories_id(self):
        return self._categories_id

    @categories_id.setter
    def categories_id(self, value):
        self._categories_id = value

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value

    @property
    def drawPath(self):
        return self._drawPath

    @drawPath.setter
    def drawPath(self, value):
        self._drawPath = value

    @property
    def rectPath(self):
        return self._rectPath

    @rectPath.setter
    def rectPath(self, value):
        self._rectPath = value

    @classmethod
    def make_item(cls, pos: tuple, size: tuple, pen: QPen, text: str, drawPath: QPainterPath = QPainterPath()):
        """制作一个新的item"""
        item = cls(list(size))
        item.drawPath = drawPath
        item.pen = QPen(pen)
        item.text = text
        item.setPos(pos[0], pos[1])
        QFont
        return item

    def boundingRect(self):
        return QRectF(0, 0, self.size[0], self.size[1])

    def paint(self, painter: QPainter, StyleOptionGraphicsItem: QStyleOptionGraphicsItem, widget=None):
        if self.selectedFlag:
            self.pen.setStyle(Qt.DashLine)
        else:
            self.pen.setStyle(Qt.SolidLine)
        width, height = self.size
        self.pen.setWidth(3)
        painter.setPen(self.pen)
        painter.setFont(self.font)
        painter.drawText(0, -3, self.text)
        self.rectPath = QPainterPath()
        self.rectPath.addRect(0, 0, width, height)
        painter.drawPath(self.rectPath)
        pass

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        if not self.lockFlag:
            width, height = self.size
            if self.scene().deleteModel:
                return
            super(ItemBase, self).mousePressEvent(event)
            self.setFlag(QGraphicsItem.ItemIsMovable, False)
            if QRectF(0, 0, 5, 5).contains(event.pos()):
                self.setCursor(Qt.SizeFDiagCursor)
                self.cursorFlag = 0
            elif QRectF(width - 5, height - 5, 5, 5).contains(event.pos()):
                self.setCursor(Qt.SizeFDiagCursor)
                self.cursorFlag = 1
            elif QRectF(width - 5, 0, 5, 5).contains(event.pos()):
                self.setCursor(Qt.SizeBDiagCursor)
                self.cursorFlag = 2
            elif QRectF(0, height - 5, 5, 5).contains(event.pos()):
                self.setCursor(Qt.SizeBDiagCursor)
                self.cursorFlag = 3
            elif QRectF(5, 0, width - 10, 5).contains(event.pos()):
                self.setCursor(Qt.SizeVerCursor)
                self.cursorFlag = 4
            elif QRectF(5, height - 5, width - 10, 5).contains(event.pos()):
                self.setCursor(Qt.SizeVerCursor)
                self.cursorFlag = 5
            elif QRectF(0, 5, 5, height - 10).contains(event.pos()):
                self.setCursor(Qt.SizeHorCursor)
                self.cursorFlag = 6
            elif QRectF(width - 5, 5, 5, height - 10).contains(event.pos()):
                self.setCursor(Qt.SizeHorCursor)
                self.cursorFlag = 7
            elif QRectF(5, 5, width - 10, height - 10).contains(event.pos()):
                self.setCursor(Qt.ArrowCursor)
                self.setFlag(QGraphicsItem.ItemIsMovable, True)
            pass

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        if not self.lockFlag:
            if self.scene().deleteModel:
                return
            super(ItemBase, self).mouseMoveEvent(event)
            pass

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        if not self.lockFlag:
            super(ItemBase, self).mouseReleaseEvent(event)
            if event.button() & Qt.LeftButton:
                self.cursorFlag = -1
            pass

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent):
        if not self.lockFlag:
            if event.modifiers() & Qt.AltModifier:
                self.setSelected(True)
            super(ItemBase, self).hoverEnterEvent(event)

    def hoverMoveEvent(self, event: QGraphicsSceneHoverEvent):
        if not self.lockFlag:
            super(ItemBase, self).hoverMoveEvent(event)
            width, height = self.size
            if event.modifiers() & Qt.AltModifier:
                self.setSelected(True)
            elif QRectF(0, 0, 5, 5).contains(event.pos()) or QRectF(width - 5, height - 5, 5, 5).contains(event.pos()):
                self.setCursor(Qt.SizeFDiagCursor)
            elif QRectF(width - 5, 0, 5, 5).contains(event.pos()) or QRectF(0, height - 5, 5, 5).contains(event.pos()):
                self.setCursor(Qt.SizeBDiagCursor)
            elif QRectF(5, 0, width - 10, 5).contains(event.pos()) or QRectF(5, height - 5, width - 10, 5).contains(
                    event.pos()):
                self.setCursor(Qt.SizeVerCursor)
            elif QRectF(0, 5, 5, height - 10).contains(event.pos()) or QRectF(width - 5, 5, 5, height - 10).contains(
                    event.pos()):
                self.setCursor(Qt.SizeHorCursor)
            elif QRectF(5, 5, width - 10, height - 10).contains(event.pos()):
                self.setCursor(Qt.ArrowCursor)
            pass

    def wheelEvent(self, event: QGraphicsSceneWheelEvent):
        if not self.lockFlag:
            super(ItemBase, self).wheelEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedHasChanged:
            self.selectedFlag = not self.selectedFlag
            self.update()
            self.itemSelectedSignal.emit()
        return super(ItemBase, self).itemChange(change, value)
