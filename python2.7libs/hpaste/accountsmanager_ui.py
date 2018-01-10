# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'accountsmanager.ui'
#
# Created: Mon Jan  8 21:34:58 2018
#      by: pyside2-uic  running on PySide2 2.0.0~alpha0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(488, 426)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.authListView = QtWidgets.QListView(self.centralwidget)
        self.authListView.setObjectName("authListView")
        self.gridLayout.addWidget(self.authListView, 0, 0, 1, 1)
        self.publicListView = QtWidgets.QListView(self.centralwidget)
        self.publicListView.setObjectName("publicListView")
        self.gridLayout.addWidget(self.publicListView, 1, 0, 1, 1)
        self.publicVerticalLayout = QtWidgets.QVBoxLayout()
        self.publicVerticalLayout.setObjectName("publicVerticalLayout")
        self.addPublicPushButton = QtWidgets.QPushButton(self.centralwidget)
        self.addPublicPushButton.setObjectName("addPublicPushButton")
        self.publicVerticalLayout.addWidget(self.addPublicPushButton)
        self.removePublicPushButton = QtWidgets.QPushButton(self.centralwidget)
        self.removePublicPushButton.setObjectName("removePublicPushButton")
        self.publicVerticalLayout.addWidget(self.removePublicPushButton)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.publicVerticalLayout.addItem(spacerItem)
        self.gridLayout.addLayout(self.publicVerticalLayout, 1, 2, 1, 1)
        self.authVerticalLayout = QtWidgets.QVBoxLayout()
        self.authVerticalLayout.setObjectName("authVerticalLayout")
        self.addAuthPushButton = QtWidgets.QPushButton(self.centralwidget)
        self.addAuthPushButton.setObjectName("addAuthPushButton")
        self.authVerticalLayout.addWidget(self.addAuthPushButton)
        self.removeAuthPushButton = QtWidgets.QPushButton(self.centralwidget)
        self.removeAuthPushButton.setObjectName("removeAuthPushButton")
        self.authVerticalLayout.addWidget(self.removeAuthPushButton)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.authVerticalLayout.addItem(spacerItem1)
        self.gridLayout.addLayout(self.authVerticalLayout, 0, 2, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 488, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "account manager", None, -1))
        self.addPublicPushButton.setText(QtWidgets.QApplication.translate("MainWindow", "add", None, -1))
        self.removePublicPushButton.setText(QtWidgets.QApplication.translate("MainWindow", "remove", None, -1))
        self.addAuthPushButton.setText(QtWidgets.QApplication.translate("MainWindow", "add", None, -1))
        self.removeAuthPushButton.setText(QtWidgets.QApplication.translate("MainWindow", "remove", None, -1))

