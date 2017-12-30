if(__name__=='__main__'):
	import os
	#path for QT dlls if run from pycharm
	os.environ['PATH']+=r';C:\Program Files\Side Effects Software\Houdini 16.0.600\bin'
	from pprint import pprint

from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *


class QAdjustedTableView(QTableView):
	itemsChanged = Signal()

	def __init__(self,parent=None):
		super(QAdjustedTableView,self).__init__(parent)

		self.verticalHeader().sectionCountChanged.connect(self.headersChanged)
		self.verticalHeader().sectionCountChanged.connect(self.headersChanged)

	def headersChanged(self):
		self.updateGeometry()
		self.itemsChanged.emit()

	def mouseDoubleClickEvent(self,event):
		event.accept()
		if(self.parent() is not None):
			self.parent().accept()

####QT
	def sizeHint(self):
		#print("wink %d %d"%(self.verticalHeader().length()+4,self.minimumSize().width()))
		return QSize(self.minimumSize().width(),self.verticalHeader().length()+4)


class QFocusedLineEdit(QLineEdit):
	def __init__(self,parent=None):
		super(QFocusedLineEdit,self).__init__(parent)

	def focusOutEvent(self,event):
		self.setFocus()
		event.accept()

	def keyPressEvent(self,event):
		if(self.parent() is not None and event.key()==Qt.Key_Up or event.key()==Qt.Key_Down):
			event.ignore() #let it be processed by parent
		else:
			super(QFocusedLineEdit,self).keyPressEvent(event)



class UiHolder(object):
	pass

class QDropdownWidget(QWidget):
	accepted = Signal(object)
	finished = Signal()


	def __init__(self,parent=None):
		super(QDropdownWidget,self).__init__(parent)
		self.ui=UiHolder()
		self.ui.mainLayout=QVBoxLayout(self)
		self.ui.mainLayout.setContentsMargins(0,0,0,0)
		self.ui.mainLayout.setSpacing(2)
		self.ui.mainLayout.setSizeConstraint(QLayout.SetMinimumSize)
		self.ui.mainView=QAdjustedTableView(self)
		self.ui.mainView.horizontalHeader().hide()
		self.ui.mainView.verticalHeader().hide()

		self.ui.mainView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

		self.ui.mainView.setMinimumSize(32, 32)
		self.setMinimumSize(32, 32)

		self.ui.mainView.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
		self.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)

		#self.resize(128,512)
		self.setWindowFlags(Qt.Popup)

		self.__model=None
		self.__proxyModel=QSortFilterProxyModel(self)
		self.__proxyModel.setSourceModel(self.__model)
		self.__proxyModel.setFilterKeyColumn(0)
		self.__proxyModel.setFilterRegExp(QRegExp("*",Qt.CaseInsensitive,QRegExp.Wildcard))
		self.ui.mainView.setModel(self.__proxyModel)

		self.ui.nameInput = QFocusedLineEdit(self)
		self.ui.nameInput.setMinimumSize(32,24)
		self.ui.nameInput.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Preferred)

		self.ui.mainLayout.addWidget(self.ui.nameInput)
		self.ui.mainLayout.addWidget(self.ui.mainView)

		#SIGNALS
		self.ui.mainView.itemsChanged.connect(self.resizeToTable)
		self.ui.nameInput.textChanged.connect(self.filterTable)

		#FINAL TOUCH
		self.setFocusProxy(self.ui.nameInput)
		self.ui.nameInput.setFocus()


	def model(self):
		return self.__model

	def setModel(self,model):
		self.__model=model
		self.__proxyModel.setSourceModel(self.__model)

	def _proxyModel(self):
		return self.__proxyModel

	@Slot()
	def resizeToTable(self):

		#hgt=self.ui.mainView.verticalHeader().length()
		#self.resize(self.size().width(),hgt+32)
		self.adjustSize()
		if (self.__model is not None):
			self.ui.mainView.setCurrentIndex(self.__proxyModel.index(0, 0))

	@Slot(str)
	def filterTable(self,filtername):
		self.__proxyModel.setFilterRegExp(QRegExp("%s"%filtername, Qt.CaseInsensitive, QRegExp.Wildcard))

####QT overrides
	def changeEvent(self, event):
		super(QDropdownWidget, self).changeEvent(event)
		if (self.isVisible() and event.type() == QEvent.ActivationChange and not self.isActiveWindow()):
			self.hide()
			event.accept()

	@Slot()
	def accept(self):
		self.accepted.emit(self.__proxyModel.mapToSource(self.ui.mainView.currentIndex()).internalPointer())
		self.hide()

	def keyPressEvent(self,event):
		if(event.key()==Qt.Key_Up):
			cid=self.ui.mainView.currentIndex()
			if(cid.row()>0):
				self.ui.mainView.setCurrentIndex(self.__proxyModel.index(cid.row()-1,cid.column()))
		elif(event.key()==Qt.Key_Down):
			cid = self.ui.mainView.currentIndex()
			if (cid.row() < self.__proxyModel.rowCount()-1):
				self.ui.mainView.setCurrentIndex(self.__proxyModel.index(cid.row() + 1, cid.column()))
		elif(event.key()==Qt.Key_Return or event.key()==Qt.Key_Enter):
			self.accept()
		elif(event.key()==Qt.Key_Escape):
			self.hide()
		event.accept()

	def hideEvent(self,event):
		self.finished.emit()