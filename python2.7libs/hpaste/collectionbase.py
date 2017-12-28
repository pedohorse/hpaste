
class CollectionItem(object):
	def __init__(self,collection,name,description,id,metadata=None):
		self.__collection=collection
		self.__name=name			#Name
		self.__desc=description		#Description
		self.__id=id				#ID inside collection
		self.__meta=metadata		#Metadata
		#wid is not stored cuz it may be generated dynamically

	def name(self):
		return self.__name

	def description(self):
		return self.__desc

	def id(self):
		return self.__id

	def metadata(self):
		return self.__meta

	def generatePublicWid(self):
		return self.__collection.genWid(self.__id)

	def content(self):
		return self.__collection.getContent(self.__id)

	def setName(self,newname):
		raise NotImplementedError('Not Yet Implemented')

	def setDescription(self,newname):
		raise NotImplementedError('Not Yet Implemented')

	def setMetadata(self,newname):
		raise NotImplementedError('Not Yet Implemented')


def defaultLogger(s,level=1):
	levels=['VERBOSE','INFO','WARNING','ERROR']
	print('%s: %s'%(levels[level],repr(s)))

class CollectionBase(object):
	def __init__(self):
		#Deriving classes should establish connections to their sources here
		pass

	def list(self):
		#this should produce list of snippets in the collection
		#the list should be a tuple of CollectionItem-s
		# note, that id is not a wid,
		raise NotImplementedError('Abstract method')

	def reinit(self):
		#this method should completely reread everything
		#rendering all existing items invalid
		raise NotImplementedError('Abstract method')

	def genWid(self,id):
		#this should generate hpaste compatible wid, that does not require collections to work
		#collections can be separated from public wids, so creating a public wid is extra functionality
		raise NotImplementedError('Abstract method')

	def getContent(self,id):
		#this should bring the raw content of the collection item.
		raise NotImplementedError('Abstract method')