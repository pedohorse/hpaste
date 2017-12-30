

def simpleLogger(s,level=1):
	levels=['VERBOSE','INFO','WARNING','ERROR']
	print('%s: %s'%(levels[level],s if isinstance(s,str) or isinstance(s,unicode) else repr(s)))

def passLogger(s,level=1):
	pass

defaultLogger=simpleLogger
