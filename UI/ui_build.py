# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'builddeckWidget.ui'
##
## Created by: Qt User Interface Compiler version 6.6.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject)
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import (QGridLayout, QWidget)

import UI.extended_ui as eui


class Ui_BuildWindow(object):
    def setupUi(self, BuildWindow):
        if not BuildWindow.objectName():
            BuildWindow.setObjectName(u"BuildWindow")
        BuildWindow.resize(800, 600)
        self.centralwidget = QWidget(BuildWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.buildspaceWidget = eui.MyOpenGLWidget(self.centralwidget)
        self.buildspaceWidget.setObjectName(u"buildspaceWidget")

        self.gridLayout.addWidget(self.buildspaceWidget, 0, 0, 1, 1)

        BuildWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(BuildWindow)

        QMetaObject.connectSlotsByName(BuildWindow)
    # setupUi

    def retranslateUi(self, BuildWindow):
        BuildWindow.setWindowTitle(QCoreApplication.translate("BuildWindow", u"Caravan", None))
    # retranslateUi

