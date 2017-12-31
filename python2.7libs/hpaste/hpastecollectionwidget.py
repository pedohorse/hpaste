import os
import json
import urllib2
import base64
import socket

import hou

from PySide2.QtCore import Slot
from PySide2.QtWidgets import QInputDialog

import hpaste
from collections.collectionwidget import CollectionWidget
from collections.collectionbase import CollectionSyncError
from collections.githubcollection import GithubCollection


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
			super(HPasteCollectionWidget.__HPasteCollectionWidget,self).__init__(parent)
			self.accepted.connect(self.doOnAccept)

		@Slot(object)
		def doOnAccept(self,item):
			if(item is None):return
			try:
				hpaste.stringToNodes(item.content())
			except Exception as e:
				hou.ui.displayMessage("could not paste: %s"%e.message,severity=hou.severityType.Warning)


		def _addItem(self,collection):
			#Please, dont throw from here!
			nodes=hou.selectedNodes()
			if(len(nodes)==0):
				hou.ui.displayMessage('selection is empty, nothing to add',severity=hou.severityType.Warning)
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
				self.model().addItemToCollection(collection,name,desc,hpaste.nodesToString(nodes))
			except CollectionSyncError as e:
				hou.ui.displayMessage('Network error occured: %s'%e.message, severity=hou.severityType.Error)


	__instance=None
	def __init__(self):
		if(HPasteCollectionWidget.__instance is None):
			HPasteCollectionWidget.__instance=HPasteCollectionWidget.__HPasteCollectionWidget()
			try:
				token=githubAuth()
			except Exception as e:
				hou.ui.displayMessage('Something went wrong.\n%s'%e.message)
				self.__instance=None
				raise RuntimeError('FAIL')

			HPasteCollectionWidget.__instance.addCollection(GithubCollection(token))

	def __getattr__(self, item):
		return getattr(HPasteCollectionWidget.__instance,item)