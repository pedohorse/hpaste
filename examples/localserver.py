#
# This is a simple example of a plugin that stores code on local server to allow
# exchanging of short snippets while with code not leaving company's subnetwork
#
import os
import random

from ..webclipboardbase import WebClipBoardBase


class LocalServer(WebClipBoardBase):
	def __init__(self):
		#in simple case - you can just put here your local temp path, and everything else should work by itself
		self.__basePath='Z:\tmp\selfCleaningFolder\"

	@classmethod
	def speedClass(self):
		return 9

	@classmethod
	def maxStringLength(self):
		return 999000000

	def genId(self, size=8):
		if (not isinstance(size, int)): raise AttributeError("size must be int")
		if (size < 1): raise RuntimeError("improper size")
		if (size > 4096): raise RuntimeError("improper size, r u fucking with me?")

		lsmo = len(self.__symbols) - 1
		id = ''
		for i in xrange(size):
			id += self.__symbols[random.randint(0, lsmo)]
		return id

	def webPackData(self, s):
		if(not isinstance(s,str)):
			s=str(s)

		id=self.genId()

		if (len(s) > self.maxStringLength()): raise RuntimeError("len of s it too big for web clipboard currently")
		try:
			with open(os.path.join(self.__basePath,id)) as f:
				f.write(s)
		except Exception as e:
			raise RuntimeError("error writing to local server: " + str(e.message))

		return id


	def webUnpackData(self, id):
		id=str(id)

		try:
			with open(os.path.join(self.__basePath,id)) as f:
				s=f.read()
		except Exception as e:
			raise RuntimeError("error reading from local server: " + e.message)

		return s
