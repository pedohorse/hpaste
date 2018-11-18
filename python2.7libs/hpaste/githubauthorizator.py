import os
import json
import urllib2
import base64
import socket
import hou

from hcollections.QDoubleInputDialog import QDoubleInputDialog
try:
	from PySide2.QtWidgets import  QMessageBox, QInputDialog
except ImportError:
	from PySide.QtGui import QMessageBox, QInputDialog

import random
import string


class GithubAuthorizator(object):
	ver = (1, 3)
	defaultdata = {'ver': '%d.%d' % ver, 'collections': [], 'publiccollections': []}
	# log:
	# ver 1.3 : added 'enabled' key to default collection entry
	defaultentry = {'user': '', 'token': '', 'enabled': True}
	defaultfilename=os.path.normpath(os.path.join(os.environ['HOUDINI_USER_PREF_DIR'],'.hpaste_githubcollection'))
	#TODO: 2 factor authorization needs to be implemented !!
	__callbacks = []

	@classmethod
	def urlopen_nt(cls, req):
		code = -1
		rep = None
		try:
			rep = urllib2.urlopen(req)
		except urllib2.HTTPError as e:
			code = e.code
		except urllib2.URLError as e:
			raise RuntimeError('unable to reach github: %s' % e.reason)

		if (code == -1): code = rep.getcode()
		return code, rep

	@classmethod
	def readAuthorizationsFile(cls):
		#reads the config file
		#if no config file - creates one

		filepath = cls.defaultfilename
		try:
			with open(filepath, 'r') as f:
				data = json.load(f)
			if 'ver' not in data: raise RuntimeError('file is not good')
			dmajor, dminor = map(lambda x: int(x), data['ver'].split('.'))
			if dmajor != cls.ver[0]: raise RuntimeError("authorization file's major version incompatible. you will have to delete the file and have it recreated from scratch")
			if dminor < cls.ver[1]:
				for ctypename in ('collections', 'publiccollections'):
					for entry in data[ctypename]:
						for entryfield in cls.defaultentry.keys():
							if entryfield not in entry:
								entry[entryfield] = cls.defaultentry[entryfield]
				data['ver'] = cls.defaultdata['ver']
				cls.writeAuthorizationFile(data)
		except:
			# file needs to be recreated
			with open(filepath, 'w') as f:
				json.dump(cls.defaultdata, f, indent=4)
			data = dict(cls.defaultdata)  # copy

		return data

	@classmethod
	def writeAuthorizationFile(cls, data):
		#writes the config file
		#should ensure data is correct
		#TODO: check the data to be correct
		filepath = cls.defaultfilename
		with open(filepath, 'w') as f:
			json.dump(data, f, indent=4)


	@classmethod
	def __sendCallbacks(cls, arg):
		for callback in cls.__callbacks:
			try:
				if (callback[0] is None):
					callback[1](arg)
				else:
					callback[1](callback[0], arg)
			except:
				continue


	@classmethod
	def newAuthorization(cls,auth=None,altparent=None):
		# appends or changes auth in file
		# auth parameter is used as default data when promped user, contents of auth will get replaced if user logins successfully
		code=0

		data=cls.readAuthorizationsFile()
		newauth=cls.defaultentry

		if(auth is not None and 'user' in auth and 'token' in auth):
			#just write to config and get the hell out
			#or maybe we can test it first...
			oldones = [x for x in data['collections'] if x['user'] == auth['user']]
			for old in oldones:
				data['collections'].remove(old)
				cls.__sendCallbacks((old, 0, 0))
			data['collections'].append(auth)
			cls.__sendCallbacks((auth, 0, 1))
			cls.writeAuthorizationFile(data)
			return True

		while True:
			defuser = auth['user'] if auth is not None else ''
			if(hou.isUIAvailable()):
				btn, (username, password) = hou.ui.readMultiInput('github authorization required. code %d'%code, ('username', 'password'), (1,),  buttons=('Ok', 'Cancel'), initial_contents=(defuser,))
			else:
				username, password, btn = QDoubleInputDialog.getUserPassword(altparent,'authorization','github authorization required. code %d'%code,'username','password',defuser)
				btn=1-btn
			if(btn!=0):
				if(auth is None):
					return False
				else:
					if(hou.isUIAvailable()):
						btn=hou.ui.displayMessage('Do you want to remove account %s from remembered?'%auth['user'], buttons=('Yes','No'), close_choice=1)
					else:
						btn = QMessageBox.question(altparent,'question','Do you want to remove account %s from remembered?'%auth['user'])
						btn = btn==QMessageBox.No
					if(btn==1):return False
					oldones = [x for x in data['collections'] if x['user'] == auth['user']]
					for old in oldones:
						data['collections'].remove(old)
						cls.__sendCallbacks((old, 0, 0))
					try:
						cls.writeAuthorizationFile(data)
					except:
						if (hou.isUIAvailable()):
							hou.ui.displayMessage("writing token to file failed!")
						else:
							QMessageBox.warning(altparent,'error',"writing token to file failed!")
					return False


			for attempt in xrange(4): #really crude way of avoiding conflicts for now
				headers={'User-Agent': 'HPaste', 'Authorization': 'Basic %s' % base64.b64encode('%s:%s' % (username, password)), 'Accept': 'application/vnd.github.v3+json'}
				postdata={ 'scopes' : ['gist'], 'note' : 'HPaste Collection Access at %s, %s'%(socket.gethostname(), ''.join(random.choice(string.ascii_letters) for _ in xrange(6))) }
				req = urllib2.Request(r'https://api.github.com/authorizations', json.dumps(postdata), headers=headers)
				code, rep = cls.urlopen_nt(req)

				if(code == 201):
					repdata=json.loads(rep.read())

					newauth['token']=repdata['token'] #TODO: check if reply is as expected
					newauth['user']=username
					if auth is None: auth={}
					for key in newauth:auth[key]=newauth[key]
					oldones=[x for x in data['collections'] if x['user']==username]
					for old in oldones:
						data['collections'].remove(old)
						cls.__sendCallbacks((old, 0, 0))

					data['collections'].append(newauth)
					cls.__sendCallbacks((newauth, 0, 1))
					try:
						cls.writeAuthorizationFile(data)
					except:
						if (hou.isUIAvailable()):
							hou.ui.displayMessage("writing token to file failed!")
						else:
							QMessageBox.warning(altparent,'error', "writing token to file failed!")
					return True
				elif(code == 422):
					#postdata was not accepted
					#so we just make another attempt of creating a token (github requires unique note)
					pass
				elif(code == 401):
					if (hou.isUIAvailable()):
						hou.ui.displayMessage('wrong username or password')
					else:
						QMessageBox.warning(altparent,'error', 'wrong username or password')
					break
			else:
				if (hou.isUIAvailable()):
					hou.ui.displayMessage('Could not receive token from github.\nDid you verify your email address?\nAlso please check and manually delete all HPaste tokens from your github account here: https://github.com/settings/tokens')
				else:
					QMessageBox.warning(altparent, 'error', 'Could not receive token from github.\nDid you verify your email address?\nAlso please check and manually delete all HPaste tokens from your github account here: https://github.com/settings/tokens')
		return False

	@classmethod
	def removeAuthorization(cls, username):
		data=GithubAuthorizator.readAuthorizationsFile()
		auths=[x for x in data['collections'] if x['user']==username]
		if(len(auths)==0):return False

		data['collections']=filter(lambda x:x['user']!=username,data['collections'])
		for auth in auths:
			cls.__sendCallbacks((auth, 0, 0))
		cls.writeAuthorizationFile(data)

		# TODO: delete the token from github!
		# The problem is that to access auths we have to use username+password basic auth again...

		return True

	@classmethod
	def newPublicCollection(cls, username=None, altparent=None):
		data = GithubAuthorizator.readAuthorizationsFile()
		if(username is not None):
			if(isinstance(username,dict)):username=username['user']
			oldones = [x for x in data['publiccollections'] if x['user'] == username]
			for old in oldones:
				data['publiccollections'].remove(old)
				cls.__sendCallbacks((old, 1, 0))
			newitem = cls.defaultentry
			newitem['user'] = username
			data['publiccollections'].append(newitem)
			cls.__sendCallbacks((newitem, 1, 1))
			cls.writeAuthorizationFile(data)
			return True

		if(hou.isUIAvailable()):
			btn, username = hou.ui.readInput('public collection name', buttons=('Ok','Cancel'), close_choice=1)
		else:
			username, btn = QInputDialog.getText(altparent,'enter name', 'public collection name')
			btn=1-int(btn)
		if(btn!=0):return False
		oldones = [x for x in data['publiccollections'] if x['user'] == username]
		data['publiccollections'] = filter(lambda x: x['user'] != username, data['publiccollections'])
		for old in oldones:
			cls.__sendCallbacks((old, 1, 0))
		newitem = cls.defaultentry
		newitem['user'] = username
		data['publiccollections'].append(newitem)
		cls.__sendCallbacks((newitem, 1, 1))
		cls.writeAuthorizationFile(data)
		return True

	@classmethod
	def removePublicCollection(cls, username):
		data = GithubAuthorizator.readAuthorizationsFile()
		oldones = [x for x in data['publiccollections'] if x['user'] == username]
		data['publiccollections'] = filter(lambda x: x['user'] != username, data['publiccollections'])
		for old in oldones:
			cls.__sendCallbacks((old, 1, 0))
		cls.writeAuthorizationFile(data)
		return True

	@classmethod
	def setAuthorizationEnabled(cls, username, state):
		state = bool(state)
		data = GithubAuthorizator.readAuthorizationsFile()
		auths = [x for x in data['collections'] if x['user'] == username]
		if (len(auths) == 0): return False
		for auth in auths:
			doCallback = auth['enabled'] != state
			auth['enabled'] = state
			cls.writeAuthorizationFile(data)
			if doCallback:
				cls.__sendCallbacks((auth, 0, 2))

	@classmethod
	def setPublicCollsctionEnabled(cls, username, state):
		state = bool(state)
		data = GithubAuthorizator.readAuthorizationsFile()
		auths = [x for x in data['publiccollections'] if x['user'] == username]
		if (len(auths) == 0): return False
		for auth in auths:
			doCallback = auth['enabled'] != state
			auth['enabled'] = state
			cls.writeAuthorizationFile(data)
			if doCallback:
				cls.__sendCallbacks((auth, 1, 2))

	@classmethod
	def testAuthorization(cls,auth):
		#auth is supposed to be a dict returned from listAuthorizations
		#TODO: probably make a dedicatid class
		headers = {'User-Agent': 'HPaste', 'Authorization': 'Token %s' % auth['token'], 'Accept': 'application/vnd.github.v3+json'}
		req = urllib2.Request(r'https://api.github.com/user', headers=headers)
		code, rep = cls.urlopen_nt(req)

		return code == 200

	@classmethod
	def listAuthorizations(cls):
		#TODO: Should be moved to a separate module with all kinds of auths
		#should return tuple of authorization dicts

		data=cls.readAuthorizationsFile()

		return tuple(data['collections'])

	@classmethod
	def listPublicCollections(cls):
		data=cls.readAuthorizationsFile()
		return data['publiccollections']

	@classmethod
	def registerCollectionChangedCallback(cls, callback):
		"""
		registers a function to be called whenever something changes to the collection or public collection lists
		callback argument will have form of a tuple: (collection, 0/1 = auth/public, 0/1/2 = removed/added/enabledChanged)
		:param callback: a touple of (object, method) or (None, function)
		:return: status (True/False)
		"""
		assert isinstance(callback, tuple) and len(callback) == 2 and callable(callback[1]), 'callable must be a tuple of object and a callable method'
		if(callback in cls.__callbacks): return  True
		cls.__callbacks.append(callback)
		return True

	@classmethod
	def unregisterCollectionChangedCallback(cls, callback):
		"""
		unregister existing callback
		:param callback: a touple of (object, method) or (None, function)
		:return: status (True/False)
		"""
		assert isinstance(callback, tuple) and len(callback) == 2 and callable(callback[1]), 'callable must be a tuple of object and a callable method'
		if (callback in cls.__callbacks):
			cls.__callbacks.remove(callback)
			return True
		return False

	@classmethod
	def clearAllCallbacks(cls):
		"""
		clear all callbacks
		:return: None
		"""
		cls.__callbacks = []
