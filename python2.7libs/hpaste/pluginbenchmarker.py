import hpastewebplugins
import hpasteweb as hw
import random
import time
from pprint import pprint

def doTest():
	pluginlist=[x for x in hpastewebplugins.pluginClassList]
	ts=''
	for i in xrange(50000):ts+=chr(random.randint(ord('A'),ord('Z')))
	#s is 50 kb
	times={}
	for i in xrange(10):
		s=ts*(i+1)
		for plug in pluginlist:
			if (plug.__name__ not in times): times[plug.__name__] = []
			try:
				t1=time.time() #we'd better use time.clock() - but it's behaviour is too platform-dependent!
				id=hw.webPack(s,[plug.__name__])
				t2=time.time()
				ss=hw.webUnpack(id)
				t3=time.time()
				if(ss!=s):raise RuntimeError("test failed")
				print('%s in progress #%d: %s'%(plug.__name__,i,str((t2-t1,t3-t2))))
				times[plug.__name__].append((t2-t1,t3-t2))
			except:
				times[plug.__name__].append(None)
		time.sleep(10)

	#totaltimes={}
	#for k in times:
	#	if(k not in totaltimes):totaltimes[k]=0
	print('------------------------------\n')
	pprint(times)
	return times