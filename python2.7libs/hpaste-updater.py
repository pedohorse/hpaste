import sys
import os
import tempfile
import zipfile
import urllib2
import shutil

def log(stuff):
	print stuff

def update(branch):
	"""
	updates current module from given github branch
	:raises: urllib2.URLError urllib2.HTTPError
	:param branch: name of the brunch
	:return: None
	"""
	assert isinstance(branch, str) or isinstance(branch, unicode), 'branch must be a string'
	branch = str(branch)

	log('updating to branch: %s' % branch)
	hpasteDirPath = r'D:\tmp\tmpst\hpaste'#os.path.join(os.path.dirname(__file__), 'hpaste')
	log('hpaste detected at: %s\n' % hpasteDirPath)

	tmpPath = tempfile.gettempdir()
	tmpZipFile = os.path.join(tmpPath, 'hpaste_branch_tmp.zip')

	log('retrieving %s from github...' % branch)
	req = urllib2.Request('https://github.com/pedohorse/hpaste/archive/{branch}.zip'.format(branch=branch), headers={'User-Agent': 'HPaste'})
	rep = urllib2.urlopen(req)
	with open(tmpZipFile, 'wb') as f:
		f.write(rep.read())
	log('done!\n')

	tmpExtractDir = tempfile.mkdtemp('hpasteupdate')
	log('extracting...')
	try:
		with zipfile.ZipFile(tmpZipFile, 'r') as ziparch:
			ziparch.extractall(tmpExtractDir)
	finally:
		os.remove(tmpZipFile)

	log('replacing...')
	try:
		#github arch creates extra dir with branch-name, lets find it instead of constructing name
		tdir = os.listdir(tmpExtractDir)
		if len(tdir)>1:
			raise RuntimeError('unexpected archieve structure')
		else:
			tdir = tdir[0]
		backupPath = None
		if os.path.exists(hpasteDirPath):
			backupPath = os.path.join(os.path.split(hpasteDirPath)[0], '__hpaste_bkp')
			os.rename(hpasteDirPath, backupPath)
		shutil.copytree(os.path.join(tmpExtractDir, tdir, 'python2.7libs', 'hpaste'), hpasteDirPath)
		if backupPath is not None:
			shutil.rmtree(backupPath)
	except OSError as e:
		log('Error!!')
		log(repr(e))
		if backupPath is not None:
			log('trying to restore...')
			os.rename(backupPath, hpasteDirPath)
			log('update failed!')
			return

	finally:
		shutil.rmtree(tmpExtractDir)
	log('All Done!')


if __name__ == '__main__':
	if len(sys.argv) == 1:
		branch = 'master'
	else:
		branch = sys.argv[1]
	update(branch)