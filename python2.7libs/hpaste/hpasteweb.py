import hpastewebplugins
import random #to shuffle plugins

def webPack(asciiText, pluginList = None, maxChunkSize = None):
	allPackids=[]
	done=False

	while(not done):
		packid=None
		if(pluginList is None):
			pluginClasses=[x for x in hpastewebplugins.pluginClassList]
			random.shuffle(pluginClasses)
			pluginClasses.sort(reverse=True, key=lambda x:x.speedClass())
		else:
			pluginClasses=[]
			for pname in pluginList:
				pluginClasses+=[x for x in hpastewebplugins.pluginClassList if x.__name__==pname]
		for cls in pluginClasses:
			try:
				packer=cls()
				chunklen=min(packer.maxStringLength(),len(asciiText))
				if(maxChunkSize is not None): chunklen=min(chunklen,maxChunkSize)
				chunk=asciiText[:chunklen]
				packid=packer.webPackData(chunk)
				asciiText = asciiText[chunklen:]
				break
			except Exception as e:
				print("error: %s" % str(e.message))
				print("failed to pack with plugin %s, looking for alternatives..."%cls.__name__)
				continue
		if(packid is None):
			print("all web packing methods failed, sorry :(")
			raise RuntimeError("couldnt web pack data")

		allPackids.append('@'.join((packid,cls.__name__)))
		done=len(asciiText)==0
		# just a failsafe:
		if(len(allPackids)>128):
			raise RuntimeError("Failsafe triggered: for some reason too many chunks. plz check the chunkSize, or your plugins for too small allowed string sizes, or your data for sanity.")

	return '#'.join(allPackids)

def webUnpack(wid):
	#just a bit cleanup the wid first, in case it was copied with extra spaces
	wid=wid.strip()
	#
	allPackids=wid.split('#')
	asciiTextParts=[]
	for awid in allPackids:
		if (awid.count('@') != 1): raise RuntimeError('given wid is not a valid wid')
		(id, cname) = awid.split('@')

		pretendents=[x for x in hpastewebplugins.pluginClassList if x.__name__==cname]
		if(len(pretendents)==0):
			raise RuntimeError("No plugins that can process this wid found")

		asciiText=None
		for cls in pretendents:
			try:
				unpacker=cls()
				asciiText=unpacker.webUnpackData(id)
				break
			except Exception as e:
				print("error: %s" % str(e.message))
				print("keep trying...")
				continue
		if(asciiText is None):
			raise RuntimeError("couldnt web unpack data")
		asciiTextParts.append(asciiText)

	return ''.join(asciiTextParts)