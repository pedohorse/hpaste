import hou
import random
import string
from Crypto.Cipher import AES  # just for blocksize and constants

try:
    from PySide2.QtWidgets import QApplication
    from PySide2 import QtCore as qtc
except:
    from PySide.QtGui import QApplication
    from PySide import QtCore as qtc

from .hpaste import stringToNodes, nodesToString, InvalidContextError
from .hpasteweb import webPack, webUnpack

from . import hpasteoptions

def hcopyweb():
    qapp = QApplication.instance()
    try:
        nodes = hou.selectedItems()
    except:
        nodes = hou.selectedNodes()

    enctype = hpasteoptions.getOption('hpasteweb.encryption_type', '')
    key = None
    encparms = {}
    if enctype == 'AES-CBC':
        key = ''.join([random.choice(string.ascii_letters + string.digits) for x in xrange(AES.block_size)])
        encparms = {'mode': AES.MODE_CBC}
        enctype = 'AES'
    if enctype is not None and key is None:
        print('Warning: unknown encryption method, disabling encryption')
        enctype = None

    try:
        s = nodesToString(nodes, encryption_type=enctype, key=key, **encparms)
    except RuntimeError as e:
        hou.ui.displayMessage("Error: %s" % str(e.message), severity=hou.severityType.Error)
        return
    except RuntimeWarning as e:  # da heck?
        hou.ui.displayMessage("Warning: %s" % str(e.message), severity=hou.severityType.Warning)
    #except Exception as e:
    #    hou.ui.displayMessage("Internal Error: %s %s" % (str(type(e)), str(e.message)), severity=hou.severityType.Error)
    #    return

    if isinstance(qapp, QApplication):
        qapp.setOverrideCursor(qtc.Qt.WaitCursor)
    try:
        s = webPack(s)
    except Exception as e:
        hou.ui.displayMessage(e.message, severity=hou.severityType.Error, title='error')
        return
    finally:
        if isinstance(qapp, QApplication):
            qapp.restoreOverrideCursor()

    # append key to snippet
    if enctype is not None:
        s = key + '!' + s
    if hou.applicationVersion()[0] > 15:
        hou.ui.copyTextToClipboard(s)
    else:
        qapp.clipboard().setText(s)
    hou.ui.setStatusMessage("Success: Cloud link copied to clipboard!")


def hpasteweb(pane=None):
    qapp = QApplication.instance()
    if hou.applicationVersion()[0] > 15:
        s = hou.ui.getTextFromClipboard()
    else:
        s = qapp.clipboard().text()

    if isinstance(qapp, QApplication):
        qapp.setOverrideCursor(qtc.Qt.WaitCursor)

    # check for compression key
    key = None
    if '!' in s:
        key, s = s.split('!', 1)
    try:
        s = webUnpack(s)
    except Exception as e:
        hou.ui.displayMessage(e.message, severity=hou.severityType.Error, title='error')
        return
    finally:
        if isinstance(qapp, QApplication):
            qapp.restoreOverrideCursor()

    try:
        stringToNodes(s, ne=pane, key=key)
    except InvalidContextError as e:
        nec, snc = e.contexts()
        if snc == 'Sop' and nec == 'Object':
            if hou.ui.displayMessage("Error: %s" % str(e.message), severity=hou.severityType.Warning, buttons=('Create geo node', 'Cancel'), default_choice=0, close_choice=1) == 0:
                geonode = e.node().createNode('geo')
                if pane is not None:
                    geonode.setPosition(pane.cursorPosition())
                stringToNodes(s, hou_parent=geonode)
        else:
            hou.ui.displayMessage("Error: %s" % str(e.message), severity=hou.severityType.Error)
            return
    except RuntimeError as e:
        hou.ui.displayMessage("Error: %s" % str(e.message), severity=hou.severityType.Error)
        return
    except RuntimeWarning as e:
        hou.ui.displayMessage("Warning: %s" % str(e.message), severity=hou.severityType.Warning)
    #except Exception as e:
    #    hou.ui.displayMessage("Internal Error: %s" % str(e.message), severity=hou.severityType.Error)
    #    return
    hou.ui.setStatusMessage("Success: Nodes pasted!")


# hpasteweb(kwargs['pane'])