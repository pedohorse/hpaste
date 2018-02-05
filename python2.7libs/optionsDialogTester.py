if(__name__=='__main__'):
	import os
	os.environ['PATH']=r'C:\Program Files\Side Effects Software\Houdini 16.0.600\bin'+r';C:\Program Files\Side Effects Software\Houdini 16.0.600\houdini\dso;'+os.environ['PATH']
	os.environ['HOUDINI_USER_PREF_DIR']=r'C:\Users\User\Documents\houdini16.0'


try:
	from PySide2.QtWidgets import *
	from PySide2.QtGui import *
	from PySide2.QtCore import *
except:
	from PySide.QtCore import *
	from PySide.QtGui import *

import sys
from hpaste.optionsdialog import OptionsDialog

if (__name__ == '__main__'):

	#os.environ['HOUDINI_USER_PREF_DIR'] = r'D:\tmp'


	QCoreApplication.addLibraryPath(r'C:\Program Files\Side Effects Software\Houdini 16.0.600\bin\Qt_plugins')
	qapp = QApplication(sys.argv)

	mw = OptionsDialog()
	mw.show()

	qapp.exec_()