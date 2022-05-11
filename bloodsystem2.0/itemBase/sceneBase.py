# encoding: utf-8
"""
@author: Soshio
@file: sceneBase.py
@time:  下午1:56
@desc:
"""
import cv2
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsSceneMouseEvent, QGraphicsSceneWheelEvent, QWidget, QGraphicsItem
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from random import choice
from itemBase.itemBase import ItemBase
from utils.utils import *


def cvimg_to_qtimg(cvimg, w, h):
    # height, width, depth = cvimg.shape
    # cvimg = cv2.cvtColor(cvimg, cv2.COLOR_BGR2RGB)
    qtimg = QImage(cvimg.data, w, h, (w * 24 + 31) // 32 * 4, QImage.Format_RGB888)

    return qtimg


class SceneBase(QGraphicsScene):
    wheelSignal = pyqtSignal(QGraphicsSceneWheelEvent)
    createItemSignal = pyqtSignal(QGraphicsSceneMouseEvent)
    changeItemSignal = pyqtSignal(QGraphicsSceneMouseEvent)
    endItemSignal = pyqtSignal(QGraphicsSceneMouseEvent)
    getProbClsSignal = pyqtSignal(ItemBase)

    def __init__(self, parent):
        self.img = QImage()
        self.img_path = None  # 保存当前显示图片的文件路径
        self.xml_path = None  # 保存
        super(SceneBase, self).__init__(parent)
        self.parent = parent
        self.Path = QPainterPath()
        self.pathStartPos = None
        self.deleteModel = False

        self.rect = QRectF(0, 0, 1200, 900)
        # self.setSceneRect(0, 0, 960, 640)
        self.setSceneRect(self.rect)
        self.setParent(self.parent)

    def set_img_from_path(self, image_path):  # 其实为原版的set_img
        self.img = QImage(image_path)
        self.img_path = image_path
        self.update()
        pass

    def set_img(self, image, w, h):
        # input cv image
        image = cvimg_to_qtimg(image, w, h)
        self.img = image
        self.update()
        pass

    def drawBackground(self, painter: QPainter, rect: QRectF):
        painter.drawImage(self.rect, self.img)
        Pen = QPen(Qt.blue)
        Pen.setWidth(3)
        painter.setPen(Pen)
        painter.drawPath(self.Path)
        if self.pathStartPos and self.Path.currentPosition():
            painter.drawLine(self.pathStartPos, self.Path.currentPosition())
        pass

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        if self.deleteModel:
            if event.buttons() & Qt.LeftButton:
                if self.itemAt(event.scenePos(), QTransform()):
                    item = self.itemAt(event.scenePos(), QTransform())
                    item.setSelected(not item.isSelected())
                self.Path.moveTo(event.scenePos())
                self.pathStartPos = event.scenePos()
                if self.focusItem():
                    item = self.focusItem()
                    item.drawPath.swap(QPainterPath())
                    item.fillColor = Qt.yellow
                    item.update()
            return
        super(SceneBase, self).mousePressEvent(event)
        if event.buttons() & Qt.RightButton:
            self.createItemSignal.emit(event)  # 因为要putItem,涉及nameList,下面三个如下
        elif self.itemAt(event.scenePos(), QTransform()) and event.buttons() & Qt.LeftButton:
            item = self.itemAt(event.scenePos(), QTransform())
            self.setFocusItem(item)
            self.getProbClsSignal.emit(item)
        pass

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        # deleteModel实现
        super(SceneBase, self).mouseMoveEvent(event)
        if self.deleteModel:
            if event.buttons() & Qt.LeftButton:
                self.Path.lineTo(event.scenePos())
                self.update()
            return
        if event.buttons() & Qt.RightButton:
            self.changeItemSignal.emit(event)
        elif self.hasFocus() and event.buttons() & Qt.LeftButton:
            item = self.focusItem()
            if not item:  # bug????
                return
            if item.cursorFlag == -1:
                return
            scene_pos = event.scenePos()
            item_pos = item.scenePos()
            item_x = item_pos.x()
            item_y = item_pos.y()
            item.prepareGeometryChange()
            if item.cursorFlag == 0:  # 左上
                item.width -= event.scenePos().x() - item.scenePos().x()
                item.height -= event.scenePos().y() - item.scenePos().y()
                item.setPos(event.scenePos())
            elif item.cursorFlag == 1:  # 右下
                item.width += event.scenePos().x() - (item.scenePos().x() + item.width)
                item.height += event.scenePos().y() - (item.scenePos().y() + item.height)
            elif item.cursorFlag == 2:  # 右上
                item.width += event.scenePos().x() - (item.scenePos().x() + item.width)
                item.height -= event.scenePos().y() - item.scenePos().y()
                item.setPos(item_x, event.scenePos().y())
            elif item.cursorFlag == 3:  # 左下
                item.width -= event.scenePos().x() - item.scenePos().x()
                item.height += event.scenePos().y() - (item.scenePos().y() + item.height)
                item.setPos(event.scenePos().x(), item_y)
            elif item.cursorFlag == 4:  # 上
                item.height -= event.scenePos().y() - item_y
                item.setPos(item_x, event.scenePos().y())
            elif item.cursorFlag == 5:  # 下
                item.height += event.scenePos().y() - (item_y + item.height)
            elif item.cursorFlag == 6:  # 左
                item.width -= event.scenePos().x() - item.scenePos().x()
                item.setPos(event.scenePos().x(), item_y)
            elif item.cursorFlag == 7:  # 右
                item.width += event.scenePos().x() - (item.scenePos().x() + item.width)
            item.update()
        pass

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        super(SceneBase, self).mouseReleaseEvent(event)
        if self.deleteModel:
            items = self.items(self.Path)
            for item in items:
                if item.lockFlag:
                    continue
                self.setFocusItem(item)  # 设置为待确定
                self.Path = item.mapFromScene(self.Path)
                self.Path = self.Path.simplified()
                # item.drawPath = self.Path.intersected(item.rectPath)
                self.Path.closeSubpath()
                self.pathStartPos = None
                item.drawPath = item.rectPath.intersected(self.Path)
                item.update()
            self.Path.swap(QPainterPath())
            self.update()
        else:
            if event.button() & Qt.RightButton:
                self.endItemSignal.emit(event)
        pass

    def event(self, event: QEvent):
        if event.type() == event.GraphicsSceneMouseMove and event.modifiers() & Qt.AltModifier:
            self.Path.lineTo(event.scenePos())
        elif event.type() == event.KeyRelease and event.key() == Qt.Key_Alt:
            self.Path.swap(QPainterPath())
        self.update()
        return super(SceneBase, self).event(event)

    def wheelEvent(self, event: QGraphicsSceneWheelEvent):
        super(SceneBase, self).wheelEvent(event)
        if not event.modifiers() & Qt.ShiftModifier:
            self.wheelSignal.emit(event)
        elif event.modifiers() & Qt.ShiftModifier:
            item = self.itemAt(event.scenePos(), QTransform())
            if item:
                if event.delta() < 0:
                    item.width += item.Sensitivity
                    item.height += item.Sensitivity
                    item.update()
                else:
                    item.width -= item.Sensitivity
                    item.height -= item.Sensitivity
                    item.update()

    def keyPressEvent(self, event: QKeyEvent):
        super(SceneBase, self).keyPressEvent(event)
        if event.key() == Qt.Key_Delete:
            for item in self.selectedItems():
                self.removeItem(item)
        elif event.key() == Qt.Key_Q:
            self.deleteModel = not self.deleteModel
            self.clearFocus()
        elif event.key() == Qt.Key_E:
            items = self.selectedItems()
            for item in items:
                item.lockFlag = 0
                item.update()
            self.update()
        elif event.key() == Qt.Key_Alt:
            self.Path.moveTo(self.parent.ui.graphicsView.mapFromGlobal(QCursor.pos()))
        elif event.key() == Qt.Key_Return:
            if self.focusItem():
                item = self.focusItem()
                item.lockFlag = 1
                item.fillColor = Qt.white
                item.update()
                self.clearFocus()

    def if_have_img(self):
        "判断当前scene有没有图片"
        if self.img_path is not None:
            return True
        return False

    def add_item(self, items):
        "向scene添加item"
        items = listy(items)
        for i in range(len(items)):
            self.addItem(items[i])
        self.update()
        pass

    def set_focus(self, item):
        self.setFocusItem(item)
        pass

    def change_item_attributes(self, items, **kwargs):
        """改变传入的items列表的某个属性"""
        items = listy(items)
        for item in items:
            item.prepareGeometryChange()
            for key, value in kwargs.items():
                if hasattr(item, key):
                    setattr(item, key, value)
            item.update()
