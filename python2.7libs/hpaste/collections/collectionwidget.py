if(__name__=='__main__'):
	import os
	os.environ['PATH']+=r';C:\Program Files\Side Effects Software\Houdini 16.0.600\bin'

	from pprint import pprint

from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from QDropdownWidget import QDropdownWidget

import collectionbase

class SnippetCollectionModel(QAbstractTableModel):
	def __init__(self,collectionsList,parent=None):
		super(SnippetCollectionModel,self).__init__(parent)
		self.__collections=list(collectionsList)
		self.__itemList=[]

		self.rescanCollections()

	def addCollection(self,collection):
		assert isinstance(collection,collectionbase.CollectionBase),'collection must be a collection'
		self.__collections.append(collection)
		self.__itemList+=collection.list()
		self.layoutChanged.emit()

	def rescanCollections(self):
		self.__itemList=[]
		for collection in self.__collections:
			self.__itemList+=collection.list()


	def columnCount(self,index):
		if (index.isValid()): return 0
		return 1

	def rowCount(self,index):
		if (index.isValid()): return 0
		return len(self.__itemList)

	def index(self,row,col,parent):
		if(parent!=QModelIndex()):
			return QModelIndex()
		return self.createIndex(row,col,self.__itemList[row])

	def data(self,index, role = Qt.DisplayRole):
		if(role==Qt.DisplayRole):
			if(index.column()>0):return ''
			return self.__itemList[index.row()].name()
		return None



class CollectionWidget(QDropdownWidget):
	def __init__(self,parent=None):
		super(CollectionWidget,self).__init__(parent)
		self.setModel(SnippetCollectionModel([],self))

	def addCollection(self,collection):
		self.model().addCollection(collection)

####TESTING
if(__name__=='__main__'):
	class FakeCollection(collectionbase.CollectionBase):

		def list(self):
			return [collectionbase.CollectionItem(self,'item %s'%x,'fat','testnoid') for x in xrange(100)]

	import sys
	from os import path
	from githubcollection import GithubCollection
	QCoreApplication.addLibraryPath(r'C:\Program Files\Side Effects Software\Houdini 16.0.600\bin\Qt_plugins')
	qapp=QApplication(sys.argv)

	#testToken = ''
	#with open(path.join(path.dirname(path.dirname(path.dirname(__file__))), 'githubtoken.tok'), 'r') as f:
	#	testToken = f.read()
	#	testToken = testToken.replace('\n', '')
	#print(testToken)
	col = FakeCollection()

	wid=CollectionWidget()
	wid.move(800, 400)
	wid.addCollection(col)
	wid.accepted.connect(lambda x: pprint(x.name()))
	wid.finished.connect(lambda : qapp.quit())
	wid.show()
	sys.exit(qapp.exec_())
