# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.6.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, QSize)
from PySide6.QtWidgets import (QGridLayout, QPushButton, QSizePolicy, QSpacerItem, QWidget)

import UI.extended_ui as eui


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setMinimumSize(QSize(800, 600))
        self.mainmenuWidget = eui.MyQWidget(MainWindow)
        self.mainmenuWidget.setObjectName(u"mainmenuWidget")
        self.mainmenuWidget.setEnabled(True)
        self.mainmenuWidget.setAutoFillBackground(False)
        self.gridLayout = QGridLayout(self.mainmenuWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 1, 2, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 300, QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.verticalSpacer, 0, 1, 1, 1)

        self.playButton = QPushButton(self.mainmenuWidget)
        self.playButton.setObjectName(u"playButton")

        self.gridLayout.addWidget(self.playButton, 1, 1, 1, 1)

        self.exitButton = QPushButton(self.mainmenuWidget)
        self.exitButton.setObjectName(u"exitButton")

        self.gridLayout.addWidget(self.exitButton, 3, 1, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 1, 0, 1, 1)

        self.builddeckButton = QPushButton(self.mainmenuWidget)
        self.builddeckButton.setObjectName(u"builddeckButton")

        self.gridLayout.addWidget(self.builddeckButton, 2, 1, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_2, 4, 1, 1, 1)

        MainWindow.setCentralWidget(self.mainmenuWidget)

        self.retranslateUi(MainWindow)
        self.exitButton.clicked.connect(MainWindow.exit)
        self.playButton.clicked.connect(MainWindow.play_game)
        self.builddeckButton.clicked.connect(MainWindow.build_deck)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Caravan", None))
        self.playButton.setText(QCoreApplication.translate("MainWindow", u"Play", None))
        self.exitButton.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.builddeckButton.setText(QCoreApplication.translate("MainWindow", u"Build Deck", None))
    # retranslateUi

