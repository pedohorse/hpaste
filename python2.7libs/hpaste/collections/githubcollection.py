import urllib2
from pprint import pprint
import base64
import json

from collectionbase import CollectionBase,CollectionItem,CollectionInconsistentError,CollectionSyncError

from logger import defaultLogger as log


def urlopen_nt(req):
	code = -1
	rep = None
	try:
		rep = urllib2.urlopen(req)
	except urllib2.HTTPError as e:
		code = e.code

	if (code == -1): code = rep.getcode()
	return code, rep

class InvalidToken(CollectionSyncError):
	def __init__(self,message):
		super(InvalidToken,self).__init__(message)

class GithubCollection(CollectionBase):


	def __init__(self, token):
		assert isinstance(token,str) or isinstance(token,unicode), 'token must be a str'

		self.__token=str(token)
		self.__headers= {'User-Agent': 'HPaste', 'Authorization':'Token %s'%self.__token}
		#{'Authorization': 'Basic %s' % base64.b64encode('%s:%s' % ('pedohorse', 'TentacleRapedH0lk'))}

		#if token is bad - we will be thrown from here with InvalidToken exception
		self.__name='invalid'
		self._rescanName()

	def test(self):
		req = urllib2.Request('https://api.github.com/authorizations', headers=self.__headers)
		rep = urllib2.urlopen(req)
		reps = rep.read()
		print(reps)
		r = json.loads(reps)
		pprint(r)

	def name(self):
		return self.__name

	def _rescanName(self):
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
		req=urllib2.Request(r'https://api.github.com/gists',headers=self.__headers)
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
				newitem=CollectionItem(self,filename,desc,'%s@%s'%(gist['id'],filename),{'raw_url':rawurl,'nettype':nettype})
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

	def changeItem(self, item, newName=None, newDescription=None, newContent=None):
		assert isinstance(item, CollectionItem), 'item must be a collection item'
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
			data['description']=newDescription
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
		item._description=gist['description']
		item._name=newfilename
		item._meta['raw_url']=gist['files'][newfilename]['raw_url']
		item._id='%s@%s'%(gist['id'],newfilename)



	def addItem(self,desiredName,description,content,metadata=None):
		assert isinstance(desiredName,str) or isinstance(desiredName,unicode), 'name should be a string'
		assert isinstance(content,str) or isinstance(content,unicode), 'conetnt shoud be a string'

		if('nettype' in metadata):
			description=":".join((metadata['nettype'],description))
		postdata = {'public': False, 'description': description}
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
		newitem=CollectionItem(self,newfilename,desc,'%s@%s' % (gist['id'], newfilename),metadata)
		return newitem

	def removeItem(self,item):
		assert isinstance(item, CollectionItem), 'item must be a collection item'
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
	with open(path.join(path.dirname(path.dirname(path.dirname(__file__))), 'githubtoken.tok'),'r') as f:
		testToken=f.read()
		testToken=testToken.replace('\n','')
	print(testToken)
	col=GithubCollection(testToken)

	res=col.list()
	for obj in res:
		log(obj.id())
	#log(res[0].content())

	#log(col.changeItem(res[0]))

