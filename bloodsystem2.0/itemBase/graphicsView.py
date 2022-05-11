# encoding: utf-8
"""
@author: red0orange
@file: graphicsView.py
@time:  上午10:37
@desc:
"""
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsObject
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from random import choice

from utils.utils import *

class GraphicsView(QGraphicsView):
    def resizeEvent(self, event: QResizeEvent) -> None:
        super(GraphicsView, self).resizeEvent(event)
        scene_width, scene_height = self.scene().width(), self.scene().height()
        show_width, show_height = self.width(), self.height()
        transform = QTransform()
        transform.scale(show_width / scene_width, show_height / scene_height)
        self.setTransform(transform, combine=False)
        pass
