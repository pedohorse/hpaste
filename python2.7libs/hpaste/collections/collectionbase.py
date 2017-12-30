
class CollectionInconsistentError(Exception):
	def __init__(self,message=''):
		super(CollectionInconsistentError,self).__init__(message)

class CollectionItemInvalidError(Exception):
	def __init__(self,message=''):
		super(CollectionItemInvalidError,self).__init__(message)

class CollectionItem(object):
	def __init__(self,collection,name,description,id,metadata=None):
		self._collection=collection
		self._name=name			#Name
		self._desc=description		#Description
		self._id=id				#ID inside collection
		self._meta=metadata		#Metadata
		self.__valid=True
		#wid is not stored cuz it may be generated dynamically

	def name(self):
		if(not self.__valid):raise CollectionItemInvalidError()
		return self._name

	def description(self):
		if (not self.__valid): raise CollectionItemInvalidError()
		return self._desc

	def id(self):
		if (not self.__valid): raise CollectionItemInvalidError()
		return self._id

	def metadata(self):
		if (not self.__valid): raise CollectionItemInvalidError()
		return self._meta

	def generatePublicWid(self):
		if (not self.__valid): raise CollectionItemInvalidError()
		return self._collection.genWid(self)

	def content(self):
		if (not self.__valid): raise CollectionItemInvalidError()
		return self._collection.getContent(self)

	def setName(self,newname):
		if (not self.__valid): raise CollectionItemInvalidError()
		self._collection.changeItem(self,newName=newname)

	def setContent(self,newcontent):
		if (not self.__valid): raise CollectionItemInvalidError()
		self._collection.changeItem(self, newContent=newcontent)

	def setDescription(self,newdescription):
		if (not self.__valid): raise CollectionItemInvalidError()
		self._collection.changeItem(self, newDescription=newdescription)

	def removeSelf(self):
		#WARNING! item will be invalidated if removed!
		self._collection.removeItem(self)

	def isValid(self):
		return self.__valid

	def _invalidate(self):
		self.__valid=False

class CollectionBase(object):
	def __init__(self):
		#Deriving classes should establish connections to their sources here
		pass

	def name(self):
		#should return some kind of readable identifier for user to see
		raise NotImplementedError('Abstract method')

	def list(self):
		#this should produce list of snippets in the collection
		#the list should be a tuple of CollectionItem-s
		# note, that id is not a wid,
		raise NotImplementedError('Abstract method')

	def reinit(self):
		#this method should completely reread everything
		#rendering all existing items invalid
		raise NotImplementedError('Abstract method')

	def genWid(self,item):
		#this should generate hpaste compatible wid, that does not require collections to work
		#collections can be separated from public wids, so creating a public wid is extra functionality
		raise NotImplementedError('Abstract method')

	def getContent(self,item):
		#this should bring the raw content of the collection item.
		raise NotImplementedError('Abstract method')

	def changeItem(self,item,newName=None,newDescription=None,newContent=None):
		#change an item
		raise NotImplementedError('Abstract method')

	def addItem(self, desiredName, description, content, metadata=None):
		#add a new item
		#should return CollectionItem
		raise NotImplementedError('Abstract method')

	def removeItem(self,item):
		#remove existing item
		raise NotImplementedError('Abstract method')