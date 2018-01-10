if(__name__=='__main__'):
	import os
	import sys
	os.environ['PATH']=r'C:\Program Files\Side Effects Software\Houdini 16.0.600\bin'+r';C:\Program Files\Side Effects Software\Houdini 16.0.600\houdini\dso;'+os.environ['PATH']
	os.environ['HOUDINI_USER_PREF_DIR']=r'C:\Users\User\Documents\houdini16.0'


	#print sys.path
	from hcollections.QDoubleInputDialog import QDoubleInputDialog



from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

import accountsmanager_ui
from githubauthorizator import GithubAuthorizator

class AccountsManager(QMainWindow):
	def __init__(self,parent):
		super(AccountsManager,self).__init__(parent)

		self.ui=accountsmanager_ui.Ui_MainWindow()
		self.ui.setupUi(self)

		data = GithubAuthorizator.listAuthorizations()
		self.__authModel=QStringListModel([x['user'] for x in data],self)
		self.ui.authListView.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.ui.authListView.setModel(self.__authModel)

		data = GithubAuthorizator.listPublicCollections()
		self.__publicModel = QStringListModel([x['user'] for x in data], self)
		self.ui.publicListView.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.ui.publicListView.setModel(self.__publicModel)

		#slots-signals
		self.ui.addAuthPushButton.clicked.connect(self.newAuth)


	def newAuth(self):
		GithubAuthorizator.newAuthorization()
		pass




if(__name__=='__main__'):
	import sys
	#testing here
	QCoreApplication.addLibraryPath(r'C:\Program Files\Side Effects Software\Houdini 16.0.600\bin\Qt_plugins')
	qapp = QApplication(sys.argv)

	wid=AccountsManager(None)
	wid.show()

	qapp.exec_()