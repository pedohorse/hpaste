import os
import json
import urllib2
import base64
import socket

import hou

from PySide2.QtCore import Slot,QSortFilterProxyModel,QRegExp,Qt
from PySide2.QtWidgets import QInputDialog,QMessageBox


import hpaste
from collections.collectionwidget import CollectionWidget
from collections.collectionbase import CollectionSyncError
from collections.githubcollection import GithubCollection
from collections.QDoubleInputDialog import QDoubleInputDialog


#TODO: add item-> menu with info edit(rename, edit description), replace content

#TODO: add confirmation on item removal

#TODO: implement some kind of collection rescan


def githubAuth():

	def urlopen_nt(req):
		code = -1
		rep=None
		try:
			rep = urllib2.urlopen(req)
		except urllib2.HTTPError as e:
			code = e.code

		if (code == -1): code = rep.getcode()
		return code,rep

	#TODO: Should be moved to a separate module with all kinds of auths
	#should return token

	#check for saved token
	defaultdata={'ver':'1.0','token':''}
	filepath=os.path.join(os.environ['HOUDINI_USER_PREF_DIR'],'.githubcollection')

	try:
		with open(filepath,'r') as f:
			data=json.load(f)
		if('token' not in data):raise RuntimeError('file is not good')
	except:
		#file needs to be recreated
		with open(filepath,'w') as f:
			json.dump(defaultdata,f,indent=4)
		data=dict(defaultdata) #copy

	token=data['token']


	#test
	headers={'User-Agent': 'HPaste', 'Authorization':'Token %s'%token}
	req=urllib2.Request(r'https://api.github.com/user',headers=headers)
	code,rep=urlopen_nt(req)

	if (code == 200): return token

	#now something is wrong
	while True:
		btn, (username, password) = hou.ui.readMultiInput('github authorization required. code %d'%code, ('username', 'password'), (1,),  buttons=('Ok', 'Cancel'))
		if(btn!=0):return None

		for attempt in xrange(10): #really crude way of avoiding conflicts for now
			headers={'User-Agent': 'HPaste', 'Authorization': 'Basic %s' % base64.b64encode('%s:%s' % (username, password))}
			postdata={'scopes':['gist'],'note':'HPaste Collection Access at %s %d'%(socket.gethostname(),attempt)}
			req = urllib2.Request(r'https://api.github.com/authorizations', json.dumps(postdata), headers=headers)
			code, rep = urlopen_nt(req)

			if(code == 201):
				repdata=json.loads(rep.read())

				data['token']=repdata['token'] #TODO: check if reply is as expected
				try:
					with open(filepath,'w') as f:
						json.dump(data,f)
				except:
					hou.ui.displayMessage("writing token to file failed!")
				return data['token']
			elif(code == 422):
				#data was not accepted
				#TODO: do
				pass
			elif(code == 401):
				hou.ui.displayMessage('wrong username or password')
				break

		hou.ui.displayMessage('could not receive token from github. please check and manually delete all HPaste tokens from your github account here: https://github.com/settings/tokens')
		return None

class HPasteCollectionWidget(object):
	class __HPasteCollectionWidget(CollectionWidget):
		def __init__(self, parent=None):
			super(HPasteCollectionWidget.__HPasteCollectionWidget,self).__init__(parent,metadataExposedKeys=('raw_url','nettype'))
			for x in xrange(1, 5):
				self.ui.mainView.horizontalHeader().hideSection(x)

			self.__nepane=None
			self.__netType=''

			self.__nettypeFilter=QSortFilterProxyModel(self)
			self.__nettypeFilter.setFilterKeyColumn(4)
			self.__nettypeFilter.setFilterRegExp(QRegExp("*", Qt.CaseInsensitive, QRegExp.Wildcard))
			self.appendFilter(self.__nettypeFilter)

			self.accepted.connect(self.doOnAccept)

		def setNetworkEditor(self,pane):
			if(not isinstance(pane,hou.NetworkEditor)):
				pane=None

			self.__nepane = pane #save to position pasted nodes in it

			if(pane is None):
				nettype='*'
				self.__netType='' #Used to create new snippet types
			else:
				nettype=hpaste.getChildContext(pane.pwd(),hou.applicationVersion())
				self.__netType=nettype
			self.__nettypeFilter.setFilterRegExp(QRegExp(nettype, Qt.CaseInsensitive, QRegExp.Wildcard))

		@Slot(object)
		def doOnAccept(self,item):
			if(item is None):return
			try:
				hpaste.stringToNodes(item.content(),ne=self.__nepane)
			except Exception as e:
				hou.ui.displayMessage("could not paste: %s"%e.message,severity=hou.severityType.Warning)


		def _addItem(self,collection):
			#Please, dont throw from here!
			nodes=hou.selectedNodes()
			if(len(nodes)==0):
				QMessageBox.warning(self,'not created','selection is empty, nothing to add')
				return

			while True:
				#btn,(name,desc) = (0,('1','2'))#hou.ui.readMultiInput('enter some information about new item',('name','description'),buttons=('Ok','Cancel'))
				name,good=QInputDialog.getText(self,'need a name','enter name for the new snippet')
				if(not good):return
				desc,good=QInputDialog.getText(self,'need description','enter description for the new snippet',text='a snippet')
				if(not good):return

				if(len(name)>0):break; #validity check

			try:
				#print(name)
				#print(desc)
				#print(hpaste.nodesToString(nodes))
				self.model().addItemToCollection(collection,name,desc,hpaste.nodesToString(nodes),metadata={'nettype':self.__netType})
			except CollectionSyncError as e:
				QMessageBox.critical(self,'something went wrong!','Network error occured: %s'%e.message)

		def _itemInfo(self, index):
			item=index.internalPointer()
			info='name: %s\n%s\ncollection id: %s\n\nmetadata:\n'%(item.name(),item.description(),item.id())
			info+='\n'.join(('%s : %s'%(key,item.metadata()[key]) for key in item.metadata()))

			QMessageBox.information(self,'item information', info)

		def _renameItem(self, index):
			item=index.internalPointer()
			oldname=item.name()
			olddesc=item.description()
			newname,newdesc,good=QDoubleInputDialog.getDoubleText(self,'modify item info','Enter new item name and description','name','description',oldname,olddesc)
			if(not good):return
			if(newname!=oldname):item.setName(newname)
			if(newdesc!=olddesc):item.setDescription(newdesc)

		def _replaceContent(self, index):
			log('_renameItem should be reimplemented in subclass to do what is needed in any specific situation', 3)

		def _confirmRemove(self,index):
			return QMessageBox.warning(self,'sure?','confirm removing the item from collection',QMessageBox.Ok|QMessageBox.Cancel) == QMessageBox.Ok


	__instance=None
	def __init__(self,parent):
		if(HPasteCollectionWidget.__instance is None):
			try:
				token=githubAuth()
			except Exception as e:
				hou.ui.displayMessage('Something went wrong.\n%s'%e.message)
				self.__instance=None
				raise RuntimeError('FAILED')
			HPasteCollectionWidget.__instance = HPasteCollectionWidget.__HPasteCollectionWidget(parent)
			HPasteCollectionWidget.__instance.addCollection(GithubCollection(token))

		elif(parent is not HPasteCollectionWidget.__instance.parent()):
			print("reparenting")
			HPasteCollectionWidget.__instance.setParent(parent)

	def __getattr__(self, item):
		return getattr(HPasteCollectionWidget.__instance,item)