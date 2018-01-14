import urllib2
import json
import copy

from collectionbase import CollectionBase,CollectionItem,CollectionInconsistentError,CollectionSyncError,CollectionItemInvalidError,CollectionItemReadonlyError,CollectionReadonlyError

from logger import defaultLogger as log


def urlopen_nt(req):
	code = -1
	rep = None
	try:
		rep = urllib2.urlopen(req)
	except urllib2.HTTPError as e:
		code = e.code
	except urllib2.URLError as e:
		raise CollectionSyncError('unable to reach collection: %s'%e.reason)

	if (code == -1): code = rep.getcode()
	return code, rep


class InvalidToken(CollectionSyncError):
	def __init__(self,message):
		super(InvalidToken,self).__init__(message)


class GithubCollection(CollectionBase):
	def __init__(self, token_or_username, public=False, token_for_public_access=None):
		assert isinstance(token_or_username,str) or isinstance(token_or_username,unicode), 'token must be a str'

		if(public):
			self.__token = None
			self.__headers = {'User-Agent': 'HPaste'}
			if(token_for_public_access is not None):
				self.__headers['Authorization']='Token %s'%token_for_public_access
			self.__readonly = True
			self.__name=token_or_username
		else:
			self.__token=str(token_or_username)
			self.__headers = {'User-Agent': 'HPaste', 'Authorization':'Token %s'%self.__token}
			self.__readonly = False

			#if token is bad - we will be thrown from here with InvalidToken exception
			self.__name='invalid'
			self._rescanName()

	def name(self):
		return self.__name

	def _rescanName(self):
		if(self.__readonly):return
		req=urllib2.Request(r'https://api.github.com/user',headers=self.__headers)
		code,rep=urlopen_nt(req)
		if (code != 200):
			if(code==403):raise InvalidToken('github auth failed')
			raise CollectionSyncError("unexpected server return level %d" % code)

		data=json.loads(rep.read())
		self.__name=data['login']

	def list(self):
		#this should produce list of snippets in the collection
		#the list should be a tuple of CollectionItem-s
		# note, that id is not a wid,
		requrl=r'https://api.github.com/gists'
		if(self.__readonly):requrl=r'https://api.github.com/users/%s/gists'%self.__name
		req=urllib2.Request(requrl,headers=self.__headers)
		code, rep = urlopen_nt(req)

		if(code!=200):
			if (code == 403): raise InvalidToken('github auth failed')
			raise CollectionSyncError("unexpected server return level %d" % code)

		log(str(rep.info()),0)
		data=json.loads(rep.read())
		gists=[x for x in data if '00_HPASTE_SNIPPET' in x['files']]
		if(len(gists)==0):
			return ()

		res=[]
		for gist in gists:
			files=gist['files']
			try:
				del files['00_HPASTE_SNIPPET']
			except KeyError:
				raise CollectionInconsistentError('impossible error! marker lost')
			if(len(files)!=1):raise CollectionInconsistentError('each gist must have one marker and one file')
			desc=gist['description']
			nettype=''
			if(':' in desc):
				nettype,desc=desc.split(':',1)

			for filename in files:
				filedata=files[filename]
				rawurl=filedata['raw_url']
				retaccess = CollectionItem.AccessType.public if gist['public'] else CollectionItem.AccessType.private
				newitem=CollectionItem(self, filename, desc, '%s@%s'%(gist['id'], filename), retaccess, self.__readonly, metadata={'raw_url':rawurl,'nettype':nettype})
				res.append(newitem)

		return tuple(res)

	def reinit(self):
		#this method should completely reread everything
		#rendering all existing items invalid
		raise NotImplementedError('Not yet implemented')

	def genWid(self,item):
		#this should generate hpaste compatible wid, that does not require collections to work
		assert isinstance(item,CollectionItem), 'item must be a collection item'

		raise NotImplementedError('Not yet implemented')

	def getContent(self,item):
		#this should bring the raw content of the collection item.
		assert isinstance(item, CollectionItem), 'item must be a collection item'

		req=urllib2.Request(item.metadata()['raw_url'],headers=self.__headers)
		code, rep = urlopen_nt(req)
		if(code!=200):
			if (code == 403): raise InvalidToken('github auth failed')
			raise CollectionSyncError("unexpected server return level %d" % code)

		data=rep.read()

		return data

	def readonly(self):
		return self.__readonly

	def changeItem(self, item, newName=None, newDescription=None, newContent=None, newAccess=None):
		assert isinstance(item, CollectionItem), 'item must be a collection item'
		#newName=str(newName)
		#newDescription=str(newDescription)
		#newContent=str(newContent)
		#just in case we have random unicode coming in
		#TODO: check that item belongs to this collection. just in case
		if (item.readonly()):raise CollectionReadonlyError()
		if (newAccess is not None and newAccess!=item.access()):
			#raise NotImplementedError('not yet implemented')

			newitem=self.addItem(item.name() if newName is None else newName, item.description() if newDescription is None else newDescription, item.content() if newContent is None else newContent,newAccess,item.metadata())
			self.removeItem(copy.copy(item))  # remove the copy cuz item gets invalidated and we dont want that for original item
			item._name = newitem._name
			item._desc = newitem._desc
			item._meta['raw_url'] = newitem._meta['raw_url']
			item._meta['nettype'] = newitem._meta['nettype']
			item._id = newitem._id
			item._access=newitem._access
			item._readonly=newitem._readonly

			#TODO: if access is changed - we have to destroy this gist and create a new one with proper 'public' key
			# Butt Beware - we need to modify item's contents and return it WITHOUT reassigning the item itself

		if('nettype' not in item.metadata()):
			item._invalidate()
			raise CollectionItemInvalidError('required metadata was not found in the item')

		id,name=item.id().split('@',1)
		data={}
		proceed=False
		if(newName is not None):
			data['filename']=newName
			proceed=True
		if(newContent is not None):
			data['content']=newContent
			proceed = True
		if(data!={}):
			data={'files':{item.name():data}}

		if(newDescription is not None):
			data['description']=':'.join((item.metadata()['nettype'],newDescription))
			proceed=True

		if (not proceed): return

		req=urllib2.Request('https://api.github.com/gists/%s'%id,json.dumps(data), headers = self.__headers)
		req.get_method=lambda : 'PATCH'
		code, rep = urlopen_nt(req)
		if (code != 200):
			if (code == 403): raise InvalidToken('github auth failed')
			raise CollectionSyncError("unexpected server return level %d" % code)

		gist=json.loads(rep.read())
		newfilenames=gist['files'].keys()
		newfilenames.remove('00_HPASTE_SNIPPET')
		if(len(newfilenames)!=1):
			raise CollectionInconsistentError('something went wrong during item changing')
		newfilename=newfilenames[0]
		desc = gist['description']
		nettype = ''
		if (':' in desc):
			nettype, desc = desc.split(':', 1)
		item._desc=desc
		item._name=newfilename
		item._meta['raw_url']=gist['files'][newfilename]['raw_url']
		item._meta['nettype']=nettype
		item._id='%s@%s'%(gist['id'],newfilename)
		item._access= CollectionItem.AccessType.public if gist['public'] else CollectionItem.AccessType.private
		item._readonly=False



	def addItem(self,desiredName,description,content, access=CollectionItem.AccessType.private, metadata=None):
		assert isinstance(desiredName,str) or isinstance(desiredName,unicode), 'name should be a string'
		assert isinstance(content,str) or isinstance(content,unicode), 'conetnt shoud be a string'
		assert access==0 or access==1, 'wrong access type'  #TODO there's no other type enforcement for this const for now

		if(self.__readonly):raise CollectionReadonlyError('collection is opened as read-only!')

		if ('nettype' not in metadata):
			raise CollectionItemInvalidError('required metadata must be present in metadata')

		description=":".join((metadata['nettype'],description))
		postdata = {'public': access==CollectionItem.AccessType.public, 'description': description}
		postdata['files'] = {'00_HPASTE_SNIPPET': {'content': 'snippets marker'}}
		postdata['files'][desiredName] = {'content':content}
		req = urllib2.Request(r'https://api.github.com/gists', json.dumps(postdata), headers=self.__headers)
		code, rep = urlopen_nt(req)
		if (code != 201):
			if (code == 403): raise InvalidToken('github auth failed')
			raise CollectionSyncError("unexpected server return level %d" % code)

		gist=json.loads(rep.read())
		newfilenames = gist['files'].keys()
		newfilenames.remove('00_HPASTE_SNIPPET')
		if (len(newfilenames) != 1):
			raise CollectionInconsistentError('something went wrong during item creating')
		newfilename = newfilenames[0]
		if(metadata is None):metadata={}
		metadata['raw_url'] = gist['files'][newfilename]['raw_url']
		desc=gist['description']
		nettype = ''
		if (':' in desc):
			nettype, desc = desc.split(':', 1)
		metadata['nettype']=nettype
		retaccess=CollectionItem.AccessType.public if gist['public'] else CollectionItem.AccessType.private
		newitem=CollectionItem(self,newfilename,desc,'%s@%s' % (gist['id'], newfilename),retaccess,False,metadata)
		return newitem

	def removeItem(self,item):
		assert isinstance(item, CollectionItem), 'item must be a collection item'
		if (item.readonly()): raise CollectionReadonlyError()

		id, name = item.id().split('@', 1)

		req = urllib2.Request(r'https://api.github.com/gists/%s'%id, headers=self.__headers)
		req.get_method=lambda : 'DELETE'
		code, rep = urlopen_nt(req)
		if (code != 204):
			if (code == 403): raise InvalidToken('github auth failed')
			raise CollectionSyncError("unexpected server return level %d" % code)

		item._invalidate()

if(__name__=='__main__'):
	from os import path
	#testing

	testToken = ''
	with open(path.join(path.dirname(path.dirname(path.dirname(path.dirname(__file__)))), 'githubtoken.tok'),'r') as f:
		testToken=f.read()
		testToken=testToken.replace('\n','')
	print(testToken)
	col=GithubCollection(testToken)

	res=col.list()
	for obj in res:
		log(obj.id())
	#log(res[0].content())

	#log(col.changeItem(res[0]))

