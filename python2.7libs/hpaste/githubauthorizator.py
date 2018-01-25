import os
import json
import urllib2
import base64
import socket
import hou

from hcollections.QDoubleInputDialog import QDoubleInputDialog
from PySide2.QtWidgets import  QMessageBox, QInputDialog

import random
import string


class GithubAuthorizator(object):
	defaultdata = {'ver': '1.2', 'collections': [], 'publiccollections': []}
	defaultentry = {'user': '', 'token': ''}
	defaultfilename=os.path.join(os.environ['HOUDINI_USER_PREF_DIR'],'.hpaste_githubcollection')
	#TODO: 2 factor authorization needs to be implemented !!

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
			if ('ver' not in data): raise RuntimeError('file is not good')
		except:
			# file needs to be recreated
			with open(filepath, 'w') as f:
				json.dump(cls.defaultdata, f, indent=4)
			data = dict(cls.defaultdata)  # copy

		return data

	@classmethod
	def writeAuthorizationFile(cls,data): #TODO: this shiuld signal hpastecollectionwidget that it needs to update
		#writes the config file
		#should ensure data is correct
		#TODO: check the data to be correct
		filepath = cls.defaultfilename
		with open(filepath, 'w') as f:
			json.dump(data, f, indent=4)


	@classmethod
	def newAuthorization(cls,auth=None,altparent=None):
		# appends or changes auth in file
		# auth parameter is used as default data when promped user, contents of auth will get replaced if user logins successfully
		code=0

		data=cls.readAuthorizationsFile()
		newauth={}

		if(auth is not None and 'user' in auth and 'token' in auth):
			#just write to config and get the hell out
			#or maybe we can test it first...
			oldones = [x for x in data['collections'] if x['user'] == auth['user']]
			for old in oldones: data['collections'].remove(old)
			data['collections'].append(auth)
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
					for old in oldones: data['collections'].remove(old)
					try:
						cls.writeAuthorizationFile(data)
					except:
						if (hou.isUIAvailable()):
							hou.ui.displayMessage("writing token to file failed!")
						else:
							QMessageBox.warning(altparent,'error',"writing token to file failed!")
					return False


			for attempt in xrange(4): #really crude way of avoiding conflicts for now
				headers={'User-Agent': 'HPaste', 'Authorization': 'Basic %s' % base64.b64encode('%s:%s' % (username, password))}
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
					for old in oldones: data['collections'].remove(old)
					data['collections'].append(newauth)
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
	def removeAuthorization(cls,username):
		data=GithubAuthorizator.readAuthorizationsFile()
		auths=[x for x in data['collections'] if x['user']==username]
		if(len(auths)==0):return False

		data['collections']=filter(lambda x:x['user']!=username,data['collections'])
		cls.writeAuthorizationFile(data)

		# TODO: delete the token from github!
		# The problem is that to access auths we have to use username+password basic auth again...

		return True

	@classmethod
	def newPublicCollection(cls,username=None, altparent=None):
		data = GithubAuthorizator.readAuthorizationsFile()
		if(username is not None):
			if(isinstance(username,dict)):username=username['user']
			newitem={'user':username}
			data['publiccollections'].append(newitem)
			cls.writeAuthorizationFile(data)
			return True

		if(hou.isUIAvailable()):
			btn, username = hou.ui.readInput('public collection name', buttons=('Ok','Cancel'), close_choice=1)
		else:
			username, btn = QInputDialog.getText(altparent,'enter name', 'public collection name')
			btn=1-int(btn)
		if(btn!=0):return False
		data['publiccollections'] = filter(lambda x: x['user'] != username, data['publiccollections'])
		data['publiccollections'].append({'user':username})
		cls.writeAuthorizationFile(data)
		return True

	@classmethod
	def removePublicCollection(cls,username):
		data = GithubAuthorizator.readAuthorizationsFile()
		data['publiccollections'] = filter(lambda x: x['user'] != username, data['publiccollections'])
		cls.writeAuthorizationFile(data)
		return True

	@classmethod
	def testAuthorization(cls,auth):
		#auth is supposed to be a dict returned from listAuthorizations
		#TODO: probably make a dedicatid class
		headers = {'User-Agent': 'HPaste', 'Authorization': 'Token %s' % auth['token']}
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