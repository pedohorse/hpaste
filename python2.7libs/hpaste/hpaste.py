import os

import hou

import json
import re
import hashlib
import binascii
import base64
import bz2

import tempfile

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


def nodesToString(nodes):
	'''
		nodes : hou.NetworkMovableItems
	algtype:
		0 - python code based algorythm
		1 - new h16 serialization, much prefered!
	:param nodes:
	:return:
	'''

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
	code = binascii.b2a_qp(code)
	# pprint(code)

	data = {}
	data['algtype'] = algtype
	data['version'] = 1
	data['houver'] = houver
	data['context'] = context
	data['code'] = code
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


def stringToNodes(s, hou_parent = None, ne = None):
	paste_to_cursor=ne is not None
	if (hou_parent is None):
		if(ne is None):
			ne = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
			if (ne is None): raise RuntimeError("cannot find opened network editor")
		hou_parent = ne.pwd()

	s = str(s)  # ununicode. there should not be any unicode in it anyways
	try:
		data = json.loads(bz2.decompress(base64.urlsafe_b64decode(s)))
	except Exception as e:
		raise RuntimeError("input data is either corrupted or just not a nodecode: " + str(e.message))

	# check version
	if (data['version'] > 1): raise RuntimeError("unsupported version of data format")

	# check accepted algtypes
	houver1 = hou.applicationVersion()
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


	if (paste_to_cursor):
		if (houver1[0] == 16):
			olditems = hou_parent.allItems()
		else:
			olditems = hou_parent.children()

	# do the work
	code = binascii.a2b_qp(code)
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
		raise RuntimeError("algorithm type is not supported")

	if(paste_to_cursor):
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
				if (pos[i] > bbmax[i]): bbmax[i] = pos[i]
				if (pos[i] < bbmin[i]): bbmin[i] = pos[i]

		cpos=cpos/cnt
		cpos[1]=bbmax[1]
		offset=ne.cursorPosition()-cpos
		for item in newitems:
			if(houver1[0] >= 16 and item.parentNetworkBox() in newitems):
				continue
			item.move(offset)


