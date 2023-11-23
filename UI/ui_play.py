# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'playWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.6.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject)
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import (QGridLayout, QWidget)

import UI.extended_ui as eui


class Ui_PlayWindow(object):
    def setupUi(self, PlayWindow):
        if not PlayWindow.objectName():
            PlayWindow.setObjectName(u"PlayWindow")
        PlayWindow.resize(800, 600)
        self.centralwidget = QWidget(PlayWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.playspaceWidget = eui.MyOpenGLWidget(self.centralwidget)
        self.playspaceWidget.setObjectName(u"playspaceWidget")

        self.gridLayout.addWidget(self.playspaceWidget, 0, 0, 1, 1)

        PlayWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(PlayWindow)

        QMetaObject.connectSlotsByName(PlayWindow)

    # setupUi

    def retranslateUi(self, PlayWindow):
        PlayWindow.setWindowTitle(QCoreApplication.translate("PlayWindow", u"Caravan", None))
    # retranslateUi
