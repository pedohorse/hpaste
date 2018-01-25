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

class AccountsManager(object):
	class __AccountsManager(QWidget):
		def __init__(self, parent, flags=0):
			super(AccountsManager.__AccountsManager,self).__init__(parent, flags)

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
			self.ui.removeAuthPushButton.clicked.connect(self.removeAuth)
			self.ui.addPublicPushButton.clicked.connect(self.newPublic)
			self.ui.removePublicPushButton.clicked.connect(self.removePublic)
			self.ui.reinitPushButton.clicked.connect(self.reinitCallback)


		def newAuth(self):
			good = GithubAuthorizator.newAuthorization()
			if(good):
				self.updateAuthList()

		def removeAuth(self):
			index = self.ui.authListView.currentIndex()
			good = GithubAuthorizator.removeAuthorization(index.data())
			if(good):
				self.updateAuthList()
				msg=QMessageBox(self)
				msg.setWindowTitle('account removed from the list!')
				msg.setTextFormat(Qt.RichText)
				msg.setText("But...<br>The access token should be deleted manually from your account.<br>Please visit <a href='https://github.com/settings/tokens'>https://github.com/settings/tokens</a> and delete access tokens you don't use anymore")
				msg.exec_()


		def newPublic(self):
			good = GithubAuthorizator.newPublicCollection()
			if (good):
				self.updatePublicList()

		def removePublic(self):
			index = self.ui.publicListView.currentIndex()
			good = GithubAuthorizator.removePublicCollection(index.data())
			if (good):
				self.updatePublicList()

		def updateAuthList(self):
			data = GithubAuthorizator.listAuthorizations()
			self.__authModel.setStringList([x['user'] for x in data])

		def updatePublicList(self):
			data = GithubAuthorizator.listPublicCollections()
			self.__publicModel.setStringList([x['user'] for x in data])

		def reinitCallback(self):
			try:
				import hpastecollectionwidget
				hpastecollectionwidget.HPasteCollectionWidget._killInstance()
			except:
				pass

	__instance=None

	def __init__(self,parent):
		if(AccountsManager.__instance is None):
			AccountsManager.__instance=AccountsManager.__AccountsManager(parent,Qt.Window)
		else:
			AccountsManager.__instance.setParent(parent)

	def __getattr__(self, item):
		return getattr(AccountsManager.__instance,item)

if(__name__=='__main__'):
	import sys
	#testing here
	QCoreApplication.addLibraryPath(r'C:\Program Files\Side Effects Software\Houdini 16.0.600\bin\Qt_plugins')
	qapp = QApplication(sys.argv)

	wid=AccountsManager(None)
	wid.show()

	qapp.exec_()