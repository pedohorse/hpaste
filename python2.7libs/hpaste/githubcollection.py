import urllib2
from pprint import pprint
import base64
import json

from collectionbase import CollectionBase,CollectionItem,defaultLogger
log=defaultLogger

class GithubCollection(CollectionBase):


	def __init__(self, token):
		assert isinstance(token,str) or isinstance(token,unicode), 'token must be a str'

		self.__token=str(token)
		self.__headers= {'User-Agent': 'HPaste', 'Authorization':'Token %s'%self.__token}
		#{'Authorization': 'Basic %s' % base64.b64encode('%s:%s' % ('pedohorse', 'TentacleRapedH0lk'))}

	def test(self):
		req = urllib2.Request('https://api.github.com/authorizations', headers=self.__headers)
		rep = urllib2.urlopen(req)
		reps = rep.read()
		print(reps)
		r = json.loads(reps)
		pprint(r)

	def list(self):
		#this should produce list of snippets in the collection
		#the list should be a tuple of CollectionItem-s
		# note, that id is not a wid,
		req=urllib2.Request(r'https://api.github.com/gists',headers=self.__headers)
		rep=urllib2.urlopen(req)
		if(rep.getcode()!=200):
			#TODO: resolve error
			log("unexpected server return level %d"%rep.getcode(),3)
			return None
		log(rep.info())
		data=json.loads(rep.read())
		gists=[x for x in data if x['description']=='HPaste snippet collection']
		if(len(gists)==0):
			# need to create new
			postdata={'public':False, 'description':'HPaste snippet collection'}
			postdata['files']={'OO_SNIPPETS':{'content':'snippets marker'}}
			req=urllib2.Request(r'https://api.github.com/gists', postdata, headers=self.__headers)
			rep = urllib2.urlopen(req)
			if (rep.getcode() != 200):
				log("unexpected server return level %d" % rep.getcode(), 3)
				return None
			return ()

		res=[]
		for gist in gists:
			files=gist['files']
			for filename in files:
				filedata=files[filename]
				desc=''
				if('description' in filedata):
					desc=filedata['description']

				newitem=CollectionItem(self,filename,desc,'%s@%s'%(gist['id'],filename))
				res.append(newitem)

		return tuple(res)



	def reinit(self):
		#this method should completely reread everything
		#rendering all existing items invalid
		raise NotImplementedError('Abstract method')

	def getWid(self,id):
		#this should generate hpaste compatible wid, that does not require collections to work
		assert isinstance(id,str) or isinstance(id,unicode), 'id must be str or unicode'
		id=str(id) #convert from unicode, actually id should not ever contain symbols above ord 127, so no need in encodings here

		raise NotImplementedError('Abstract method')

if(__name__=='__main__'):
	#testing
	testToken = '90fe706ea9de9e401427dcb75252f006acdfb96d'
	col=GithubCollection(testToken)

	res=col.list()
	for obj in res:
		log(obj.id())