import urllib2
import json

from ..webclipboardbase import WebClipBoardBase, WebClipBoardWidNotFound
from .. import hpasteoptions as opt


class HPaste(WebClipBoardBase):
	def __init__(self):
		self.__headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}

	@classmethod
	def speedClass(cls):
		return opt.getOption('hpasteweb.plugins.%s.speed_class'%cls.__name__, 10)

	@classmethod
	def maxStringLength(self):
		return 400000

	def webPackData(self, s):
		if (not isinstance(s, str)):
			s = str(s)
		if (len(s) > self.maxStringLength()): raise RuntimeError("len of s it too big for web clipboard currently")

		try:
			req = urllib2.Request(r"https://hou-hpaste.herokuapp.com/documents", s, headers=self.__headers)
			rep = urllib2.urlopen(req, timeout=30)
			repstring = rep.read()
		except Exception as e:
			raise RuntimeError("error/timeout connecting to web clipboard: " + str(e.message))

		if (rep.getcode() != 200): raise RuntimeError("error code from web clipboard")

		try:
			repson = json.loads(repstring)
			id=repson['key']
		except Exception as e:
			raise RuntimeError("Unknown Server responce: "+str(e.message))

		return str(id)


	def webUnpackData(self, id):
		id=str(id)
		try:
			req = urllib2.Request(r"https://hou-hpaste.herokuapp.com/raw/" + id, headers=self.__headers)
			rep = urllib2.urlopen(req, timeout=30)
		except urllib2.HTTPError as e:
			if e.code == 404:
				raise WebClipBoardWidNotFound(id)
			raise RuntimeError("error connecting to web clipboard: " + e.message)
		except Exception as e:
			raise RuntimeError("error/timeout connecting to web clipboard: " + e.message)

		if (rep.getcode() != 200): raise RuntimeError("error code from web clipboard")

		repstring = rep.read()

		return repstring
