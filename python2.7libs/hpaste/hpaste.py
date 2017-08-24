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


def nodesToString(nodes):
	'''
	algtype:
		0 - python code based algorythm
		1 - new h16 serialization, much prefered!
	:param nodes:
	:return:
	'''

	parent = nodes[0].parent()
	for node in nodes:
		if (node.parent() != parent): raise RuntimeError("selected nodes must have the same parent!")

	algtype = 1
	houver = hou.applicationVersion()
	if (houver[0] == 15 and houver[1] == 0 or houver[0] < 15):
		raise RuntimeError("sorry, unsupported for now")
	elif (houver[0] == 15 and houver[1] == 5):
		algtype = 1
	elif (houver[0] >= 16):
		algtype = 2

	#print("using algorithm %d"%algtype)
	if (algtype == 0):
		nodes = orderNodes(nodes)

	context = parent.type().childTypeCategory().name()

	code = ''
	if (algtype == 0):
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
				nodes[0].parent().saveChildrenToFile(nodes, (), temppath)
			if (algtype == 2):
				nodes[0].parent().saveItemsToFile(nodes, temppath, False) #true or false....
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
	stringdata = base64.urlsafe_b64encode(bz2.compress(json.dumps(data)))

	return stringdata


def stringToNodes(s, hou_parent=None):
	if (hou_parent is None):
		ne = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
		if (ne is None): raise RuntimeError("cannot find opened network editor")
		hou_parent = ne.pwd()

	s = str(s)  # ununicode. there should not be any unicode in it anyways
	try:
		data = json.loads(bz2.decompress(base64.urlsafe_b64decode(s)))
	except Exception as e:
		print("input data is either corrupted or just not a nodecode: " + e.message)
		return

	# check version
	if (data['version'] > 1): raise RuntimeError("unsupported version of data format")

	# check accepted algtypes
	houver1 = hou.applicationVersion()
	supportedAlgs = set()
	if (houver1[0] == 15 and houver1[1] == 5):
		supportedAlgs.add(0)
		supportedAlgs.add(1)
	if (houver1[0] >= 16):
		supportedAlgs.add(0)
		supportedAlgs.add(1)
		supportedAlgs.add(2)
	algtype = data['algtype']
	if (algtype not in supportedAlgs): raise RuntimeError(
		"algorithm type is not supported by this houdini version, :( ")

	# check hou version
	houver2 = data['houver']
	if (houver1[0] != houver2[0] or houver1[1] != houver2[1]): print(
	"HPaste: WARNING!! nodes were copied from a different houdini version: " + str(houver2))

	# check context
	context = hou_parent.type().childTypeCategory().name()
	if (context != data['context']): raise RuntimeError("this snippet has '%s' context" % data['context'])

	# check sum
	code = data['code']
	if (hashlib.sha1(code).hexdigest() != data['chsum']):
		raise RuntimeError("checksum failed!")

	# do the work
	code = binascii.a2b_qp(code)
	if (algtype == 0):
		# high security risk!!
		if (hou.isUiAvailable()):
			ok = hou.ui.displayMessage(
				"WARNING! The algorith type used by the pasted snipped is legacy and present HIGH SECURITY RISK!\n be sure you TRUST THE SOURCE of the snippet!",
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
					hou_parent.loadItemsFromFile(temppath)
			except hou.LoadWarning as e:
				msg = e.instanceMessage()
				print(msg)
				if (hou.isUiAvailable()):
					# truncate just for display with random number 253
					msgtrunc = False
					if (len(msg) > 253):
						msgtrunc = True
						msg = msg[:253] + "..."
					hou.ui.displayMessage("There were warnings during load" + (
					"(see console for full message)" if msgtrunc else "") + "\n" + msg)
		finally:
			os.close(fd)
