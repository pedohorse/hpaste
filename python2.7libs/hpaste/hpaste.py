import os

import hou

import json
import re
import hashlib
import binascii
import base64
import bz2

import tempfile

opt = None
try:
	import hpasteoptions as opt
except:
	print("Hpaste: Failed to load options, using defaults")
# for debug
from pprint import pprint


def orderSelected():
	return orderNodes(hou.selectedNodes())


def orderNodes(nodes):
	'''
	take a list of nodes, return a specially sorted list of nodes in order to proprely recreate them later
	'''
	if (len(nodes) == 0): return []

	parent = nodes[0].parent()
	for node in nodes:
		if (node.parent() != parent): raise RuntimeError("selected nodes must have the same parent!")

	snodes = [x for x in nodes if len([y for y in x.inputs() if y in nodes]) == 0]  # init with leaf nodes

	for node in snodes:
		for output in (x for x in node.outputs() if x in nodes):
			if (output in snodes): snodes.remove(output)  # TODO: uff.... maybe there's a more optimized way?
			snodes.append(output)

	return snodes


def getChildContext(node,houver):
	if(houver[0]>=16):
		return node.type().childTypeCategory().name()
	elif(houver[0]<=15 and houver>=10):
		return node.childTypeCategory().name()
	else: raise RuntimeError("unsupported houdini version!")


def nodesToString(nodes, transfer_assets = None):
	'''
		nodes : hou.NetworkMovableItems
	algtype:
		0 - python code based algorythm
		1 - new h16 serialization, much prefered!
	:param nodes:
	:return:
	'''

	if (transfer_assets is None):
		transfer_assets = True
		if(opt is not None):
			transfer_assets = opt.getOption('hpaste.transfer_assets', transfer_assets)


	parent = nodes[0].parent()
	for node in nodes:
		if (node.parent() != parent): raise RuntimeError("selected items must have the same parent!")

	algtype = 1
	houver = hou.applicationVersion()
	if (houver[0] < 10):
		raise RuntimeError("sorry, unsupported for now")
	elif (houver[0] <= 15 and houver[0] >= 10):
		algtype = 1
	elif (houver[0] >= 16):
		algtype = 2

	# print("using algorithm %d"%algtype)
	if (algtype == 0):
		nodes = orderNodes(nodes)

	context = getChildContext(parent,houver)

	code = ''
	hdaList = []
	if (algtype == 0):
		# filter to keep only nodes
		nodes = [x for x in nodes if isinstance(x,hou.Node)]
		for node in nodes:
			newcode = node.asCode(recurse=True)
			if (len(node.inputs()) > 0):
				# there's a bug(from our pov) of name clashing for default connection code for top node
				newcode = re.sub(r'# Code to establish connections for.+\n.+\n', '# filtered lines\n', newcode, 1)
			code += newcode
	elif (algtype == 1 or algtype == 2):
		if(transfer_assets): # added in version 2.1
			# scan for nonstandard asset definitions
			hfs = os.environ['HFS']
			for elem in nodes:
				if (not isinstance(elem, hou.Node)): continue
				for node in [elem] + list(elem.allSubChildren()):
					definition = node.type().definition()
					if (definition is None): continue
					libpath = definition.libraryFilePath()
					if (libpath.startswith(hfs)): continue
					# at this point we've got a non standard asset definition
					#print(libpath)
					fd, temppath = tempfile.mkstemp()
					try:
						definition.copyToHDAFile(temppath)
						with open(temppath, 'rb') as f:
							hdacode = f.read()
						hdaList.append({'type':node.type().name(), 'category':node.type().category().name(), 'code':base64.b64encode(hdacode)})
					finally:
						os.close(fd)

		# get temp file
		fd, temppath = tempfile.mkstemp()
		try:
			if (algtype == 1):
				#filter to keep only nodes
				nodes = [x for x in nodes if isinstance(x, hou.Node)]
				nodes[0].parent().saveChildrenToFile(nodes, (), temppath)
			if (algtype == 2):
				nodes[0].parent().saveItemsToFile(nodes, temppath, False)  # true or false....
			with open(temppath, "rb") as f:
				code = f.read()
		finally:
			os.close(fd)
	# THIS WAS IN FORMAT VERSION 1 code = binascii.b2a_qp(code)
	code = base64.b64encode(code)
	# pprint(code)

	data = {}
	data['algtype'] = algtype
	data['version'] = 2
	data['version.minor'] = 1
	data['houver'] = houver
	data['context'] = context
	data['code'] = code
	data['hdaList'] = hdaList
	data['chsum'] = hashlib.sha1(code).hexdigest()
	#security entries, for future
	data['author'] = 'unknown'
	data['encrypted'] = False
	data['encryptionType'] = ''
	data['signed'] = False
	data['signatureType'] = ''
	#these suppose there is a trusted vendors list with their public keys stored

	stringdata = base64.urlsafe_b64encode(bz2.compress(json.dumps(data)))

	return stringdata


def stringToNodes(s, hou_parent = None, ne = None, ignore_hdas_if_already_defined = None, force_prefer_hdas = None, override_network_position = None):
	'''
	TODO: here to be a docstring
	:param s:
	:param hou_parent:
	:param ne:
	:param ignore_hdas_if_already_defined:
	:param force_prefer_hdas:
	:override_network_position: hou.Vector2 - position in networkview pane
	:return:
	'''
	if (ignore_hdas_if_already_defined is None):
		ignore_hdas_if_already_defined = True
		if(opt is not None):
			ignore_hdas_if_already_defined = opt.getOption('hpaste.ignore_hdas_if_already_defined', ignore_hdas_if_already_defined)

	if (force_prefer_hdas is None):
		force_prefer_hdas = False
		if(opt is not None):
			force_prefer_hdas = opt.getOption('hpaste.force_prefer_hdas', force_prefer_hdas)

	s = str(s)  # ununicode. there should not be any unicode in it anyways
	try:
		data = json.loads(bz2.decompress(base64.urlsafe_b64decode(s)))
	except Exception as e:
		raise RuntimeError("input data is either corrupted or just not a nodecode: " + str(e.message))

	houver1 = hou.applicationVersion()

	paste_to_position = ne is not None or override_network_position is not None
	if (hou_parent is None):
		if(ne is None):
			nes = [x for x in hou.ui.paneTabs() if x.type() == hou.paneTabType.NetworkEditor and getChildContext(x.pwd(), houver1) == data['context']]
			if (len(nes)==0): raise RuntimeError("this snippet has '{0}' context. cannot find opened network editor with context '{0}' to paste in".format(data['context']))
			ne = nes[0]
		hou_parent = ne.pwd()

	# check version
	formatVersion=data['version']
	if (formatVersion > 2): raise RuntimeError("unsupported version of data format. Try updating hpaste to the latest version")

	# check accepted algtypes
	supportedAlgs = set()
	if (houver1[0] == 15):
		supportedAlgs.add(0)
		supportedAlgs.add(1)
		supportedAlgs.add(2) #WITH BIG WARNING!!!
	if (houver1[0] >= 16):
		supportedAlgs.add(0)
		supportedAlgs.add(1)
		supportedAlgs.add(2)
	algtype = data['algtype']
	if (algtype not in supportedAlgs): raise RuntimeError("algorithm type is not supported by this houdini version, :( ")

	# check hou version
	houver2 = data['houver']
	if (houver1[0] != houver2[0] or houver1[1] != houver2[1]): print("HPaste: WARNING!! nodes were copied from a different houdini version: " + str(houver2))

	# check context
	context = getChildContext(hou_parent,houver1)
	if (context != data['context']): raise RuntimeError("this snippet has '%s' context" % data['context'])

	# check sum
	code = data['code']
	if (hashlib.sha1(code).hexdigest() != data['chsum']):
		raise RuntimeError("checksum failed!")


	if (paste_to_position):
		if (houver1[0] >= 16):
			olditems = hou_parent.allItems()
		else:
			olditems = hou_parent.children()

	# do the work
	for hdaitem in data.get('hdaList',[]): # added in version 2.1
		hdacode = base64.b64decode(hdaitem['code'])
		ntype = hdaitem['type']
		ncategory = hdaitem['category']
		if (ignore_hdas_if_already_defined):
			nodeType = hou.nodeType(hou.nodeTypeCategories()[ncategory],ntype)
			if(nodeType is not None):
				#well, that's already a bad sign, means it is installed
				continue

		fd, temppath = tempfile.mkstemp()
		try:
			with open(temppath, 'wb') as f:
				f.write(hdacode)
			for hdadef in hou.hda.definitionsInFile(temppath):
				hdadef.copyToHDAFile('Embedded')
				#hdadef.save('Embedded')
		finally:
			os.close(fd)

		if(force_prefer_hdas):
			embhdas = [x for x in hou.hda.definitionsInFile("Embedded") if (x.nodeType().name() == ntype and x.nodeTypeCategory().name() == ncategory)]
			if(len(embhdas)==1):
				embhdas[0].setIsPreferred(True)

	#now nodes themselves
	if(formatVersion == 1):
		code = binascii.a2b_qp(code)
	elif(formatVersion >= 2):
		code = base64.b64decode(code)
	else:
		raise RuntimeError("Very unexpected format version in a very inexpected place!")

	if (algtype == 0):
		# high security risk!!
		if (hou.isUiAvailable()):
			ok = hou.ui.displayMessage(
				"WARNING! The algorithm type used by the pasted snipped is legacy and present HIGH SECURITY RISK!\n be sure you TRUST THE SOURCE of the snippet!",
				("CANCEL", "ok"), severity=hou.severityType.Warning, close_choice=0, title="SECURITY WARNING")
		else:
			ok = 0
			print("for now u cannot paste SECURITY RISK snippets in non-interactive mode")
		if (ok != 1): return

		exec (code, {}, {'hou': hou, 'hou_parent': hou_parent})
	elif (algtype == 1 or algtype == 2):
		# get temp file
		fd, temppath = tempfile.mkstemp()
		try:
			with open(temppath, "wb") as f:
				f.write(code)
			try:
				if (algtype == 1):
					hou_parent.loadChildrenFromFile(temppath)
				if (algtype == 2):
					try:
						hou_parent.loadItemsFromFile(temppath)
					except AttributeError:
						print("WARNING!!! your hou version does not support algorithm used for copying, TRYING possibly partly backward-INCOMPATIBLE method!")
						print("CHECK SCENE INTEGRITY")
						hou_parent.loadChildrenFromFile(temppath)
			except hou.LoadWarning as e:
				msg = e.instanceMessage()
				print(msg)

				# truncate just for display with random number 253
				msgtrunc = False
				if (len(msg) > 253):
					msgtrunc = True
					msg = msg[:253] + "..."
				raise RuntimeWarning("There were warnings during load" + ("(see console for full message)" if msgtrunc else "") + "\n" + msg)
		finally:
			os.close(fd)
	else:
		raise RuntimeError("algorithm type is not supported. Try updating hpaste to the latest version")

	if(paste_to_position):
		#now collect pasted nodes
		if (houver1[0] >= 16):
			newitems = [x for x in hou_parent.allItems() if x not in olditems]
		else:
			newitems = [x for x in hou_parent.children() if x not in olditems]

		if(len(newitems)==0):return
		#calc center
		cpos = hou.Vector2()
		bbmin = hou.Vector2()
		bbmax = hou.Vector2()
		cnt=0
		for item in newitems:
			cnt+=1
			pos=item.position()
			cpos+=pos
			for i in [0,1]:
				if (pos[i] > bbmax[i] or cnt==1): bbmax[i] = pos[i]
				if (pos[i] < bbmin[i] or cnt==1): bbmin[i] = pos[i]

		cpos=cpos/cnt
		cpos[1]=bbmax[1]
		if override_network_position is None:
			offset = ne.cursorPosition() - cpos
		else:
			offset = override_network_position - cpos
		for item in newitems:
			if(houver1[0] >= 16 and item.parentNetworkBox() in newitems):
				continue
			item.move(offset)


