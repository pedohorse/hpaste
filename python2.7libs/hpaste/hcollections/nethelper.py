import urllib2
import collectionbase
from logger import defaultLogger as log

class ErrorReply(object):
	def __init__(self, code, headers=None, msg=''):
		if headers is None:
			headers = {}
		self.__headers = headers
		self.__code = code
		self.msg = msg

	def info(self):
		return self.__headers

	def read(self):
		return None


def urlopen_nt(req, fallback_cert=0):
	code = -1
	rep = None
	try:
		rep = urllib2.urlopen(req)
	except urllib2.HTTPError as e:
		code = e.code
		rep = ErrorReply(code, e.headers, e.msg)
	except urllib2.URLError as e:
		try:
			if fallback_cert == 0:
				import certifi
				rep = urllib2.urlopen(req, cafile=certifi.where())
			elif fallback_cert == 1:
				import ssl
				rep = urllib2.urlopen(req, context=ssl._create_unverified_context())
				log("connected with unverified context", 2)
			else:
				raise collectionbase.CollectionSyncError('unable to reach collection: %s' % e.reason)
		except urllib2.URLError as e1:
			urlopen_nt(req, fallback_cert+1)

	if code == -1:
		code = rep.getcode()
	return code, rep
