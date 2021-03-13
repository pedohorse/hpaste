# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'accountsmanager.ui'
#
# Created: Sat Jan 27 19:14:29 2018
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(488, 426)
        MainWindow.setStyleSheet("QWidget#MainWindow {\n"
"    background-color : rgb(78,78,78)\n"
"}")
        self.verticalLayout = QtGui.QVBoxLayout(MainWindow)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.publicVerticalLayout = QtGui.QVBoxLayout()
        self.publicVerticalLayout.setObjectName("publicVerticalLayout")
        self.addPublicPushButton = QtGui.QPushButton(MainWindow)
        self.addPublicPushButton.setObjectName("addPublicPushButton")
        self.publicVerticalLayout.addWidget(self.addPublicPushButton)
        self.removePublicPushButton = QtGui.QPushButton(MainWindow)
        self.removePublicPushButton.setObjectName("removePublicPushButton")
        self.publicVerticalLayout.addWidget(self.removePublicPushButton)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.publicVerticalLayout.addItem(spacerItem)
        self.gridLayout.addLayout(self.publicVerticalLayout, 1, 2, 1, 1)
        self.authListView = QtGui.QListView(MainWindow)
        self.authListView.setObjectName("authListView")
        self.gridLayout.addWidget(self.authListView, 0, 0, 1, 1)
        self.authVerticalLayout = QtGui.QVBoxLayout()
        self.authVerticalLayout.setObjectName("authVerticalLayout")
        self.addAuthPushButton = QtGui.QPushButton(MainWindow)
        self.addAuthPushButton.setObjectName("addAuthPushButton")
        self.authVerticalLayout.addWidget(self.addAuthPushButton)
        self.removeAuthPushButton = QtGui.QPushButton(MainWindow)
        self.removeAuthPushButton.setObjectName("removeAuthPushButton")
        self.authVerticalLayout.addWidget(self.removeAuthPushButton)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.authVerticalLayout.addItem(spacerItem1)
        self.gridLayout.addLayout(self.authVerticalLayout, 0, 2, 1, 1)
        self.publicListView = QtGui.QListView(MainWindow)
        self.publicListView.setObjectName("publicListView")
        self.gridLayout.addWidget(self.publicListView, 1, 0, 1, 1)
        self.reinitPushButton = QtGui.QPushButton(MainWindow)
        self.reinitPushButton.setObjectName("reinitPushButton")
        self.gridLayout.addWidget(self.reinitPushButton, 2, 2, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "account manager", None, QtGui.QApplication.UnicodeUTF8))
        self.addPublicPushButton.setText(QtGui.QApplication.translate("MainWindow", "add", None, QtGui.QApplication.UnicodeUTF8))
        self.removePublicPushButton.setText(QtGui.QApplication.translate("MainWindow", "remove", None, QtGui.QApplication.UnicodeUTF8))
        self.addAuthPushButton.setText(QtGui.QApplication.translate("MainWindow", "add", None, QtGui.QApplication.UnicodeUTF8))
        self.removeAuthPushButton.setText(QtGui.QApplication.translate("MainWindow", "remove", None, QtGui.QApplication.UnicodeUTF8))
        self.reinitPushButton.setText(QtGui.QApplication.translate("MainWindow", "re-initialize\n"
"collections", None, QtGui.QApplication.UnicodeUTF8))

