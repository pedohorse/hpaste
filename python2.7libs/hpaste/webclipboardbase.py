
class WebClipBoardBase(object):
	def maxStringLength(self):
		'''
		Keep in mind - this is about ascii string, so it should be equal to max data size in bytes
		:return: max string length
		'''
		raise NotImplementedError()

	def webPackData(self, s):
		raise NotImplementedError()

	def webUnpackData(self, s):
		raise NotImplementedError()
