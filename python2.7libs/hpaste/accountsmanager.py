if(__name__=='__main__'):
	import os
	os.environ['PATH']+=r';C:\Program Files\Side Effects Software\Houdini 16.0.600\bin'

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

import accountsmanager_ui


class AccountsManager(QMainWindow):
	def __init__(self,parent):
		super(AccountsManager,self).__init__(parent)

		self.ui=accountsmanager_ui.Ui_MainWindow()
		self.ui.setupUi(self)





if(__name__=='__main__'):
	import sys
	#testing here
	QCoreApplication.addLibraryPath(r'C:\Program Files\Side Effects Software\Houdini 16.0.600\bin\Qt_plugins')
	qapp = QApplication(sys.argv)

	wid=AccountsManager(None)
	wid.show()

	qapp.exec_()