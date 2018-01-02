if(__name__=='__main__'):
	import os
	os.environ['PATH']+=r';C:\Program Files\Side Effects Software\Houdini 16.0.600\bin'
	from PySide2.QtCore import *

from PySide2.QtWidgets import *


class QDoubleInputDialog(QDialog):
	def __init__(self,parent=None):
		super(QDoubleInputDialog,self).__init__(parent)

		self.ui_mainLayout=QGridLayout(self)
		self.ui_text=QLabel(self)
		self.ui_label1 = QLabel(self)
		self.ui_label2 = QLabel(self)
		self.ui_line1 = QLineEdit(self)
		self.ui_line2 = QLineEdit(self)

		self.ui_buttonLayout=QHBoxLayout()
		self.ui_buttonOk = QPushButton('Ok',self)
		self.ui_buttonOk.setDefault(True)
		self.ui_buttonCancel = QPushButton('Cancel',self)
		self.ui_buttonLayout.addStretch()
		self.ui_buttonLayout.addWidget(self.ui_buttonOk)
		self.ui_buttonLayout.addWidget(self.ui_buttonCancel)

		self.ui_mainLayout.addWidget(self.ui_text, 0, 0, 1, 2)
		self.ui_mainLayout.addWidget(self.ui_label1, 1, 0)
		self.ui_mainLayout.addWidget(self.ui_label2, 2, 0)
		self.ui_mainLayout.addWidget(self.ui_line1, 1, 1)
		self.ui_mainLayout.addWidget(self.ui_line2, 2, 1)
		self.ui_mainLayout.addLayout(self.ui_buttonLayout, 3, 1)

		#Signals-Slots
		self.ui_buttonOk.clicked.connect(self.accept)
		self.ui_buttonCancel.clicked.connect(self.reject)

		#defaults
		self.ui_text.setText('Woof')
		self.ui_label1.setText('label1')
		self.ui_label2.setText('label2')

	@classmethod
	def getDoubleText(cls,parent,title,text,label1,label2,defValue1='',defVaule2=''):
		dialog=QDoubleInputDialog(parent)
		dialog.setWindowTitle(title)
		dialog.ui_text.setText(text)
		dialog.ui_label1.setText(label1)
		dialog.ui_label2.setText(label2)
		dialog.ui_line1.setText(defValue1)
		dialog.ui_line2.setText(defVaule2)

		res=dialog.exec_()
		return (res,dialog.ui_line1.text(),dialog.ui_line2.text())


if(__name__=='__main__'):
	import sys
	#testing here
	QCoreApplication.addLibraryPath(r'C:\Program Files\Side Effects Software\Houdini 16.0.600\bin\Qt_plugins')
	qapp = QApplication(sys.argv)


	print(QDoubleInputDialog.getDoubleText(None,'woof','bark on me twice','first one','and the second one','bark1','bark2'))
	#sys.exit(qapp.exec_())