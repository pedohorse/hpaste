import re
import json
import urllib2
from nethelper import urlopen_nt
try:
    from PySide2.QtWidgets import QDialog, QVBoxLayout, QLabel, QSizePolicy
    from PySide2.QtWebEngineWidgets import QWebEngineView
    from PySide2.QtCore import QUrl
except ImportError:
    raise NotImplementedError('web auth implemented only for QT5. Sorry, people who still use houdini 16.5. You will have to create access token manually. contact me to ask how.')

import time


class QGithubDeviceAuthDialog(QDialog):
    def __init__(self, client_id='42e8e8e9d844e45c2d05', parent=None):
        super(QGithubDeviceAuthDialog, self).__init__(parent=parent)
        self.setWindowTitle('Log into your GitHub account and enter this code')

        self.__webview = QWebEngineView(parent=self)
        self.__webview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.__webview.urlChanged.connect(self.on_url_changed)

        self.__devidlabel = QLabel(parent=self)
        ff = self.__devidlabel.font()
        ff.setPointSize(64)
        self.__devidlabel.setFont(ff)

        self.__layout = QVBoxLayout()
        self.setLayout(self.__layout)
        self.__layout.addWidget(self.__devidlabel)
        self.__layout.addWidget(self.__webview)
        self.__result = None

        # init auth process
        self.__client_id = client_id
        self.__headers = {'User-Agent': 'HPaste', 'Accept': 'application/json', 'Content-Type': 'application/json'}
        reqdata = {'client_id': self.__client_id, 'scope': 'gist'}
        req = urllib2.Request('https://github.com/login/device/code', data=json.dumps(reqdata), headers=self.__headers)
        req.get_method = lambda: 'POST'
        code, ret = urlopen_nt(req)
        if code != 200:
            raise RuntimeError('code %d when trying to register device' % code)
        init_data = json.loads(ret.read())
        print(init_data)
        self.__device_code = init_data['device_code']
        self.__interval = init_data.get('interval', 5)
        self.__webview.load(QUrl(init_data['verification_uri']))
        self.__devidlabel.setText('code: %s' % (init_data['user_code'],))

    def get_result(self):
        return self.__result

    def closeEvent(self, event):
        # here we assume user has done his part, so lets get checking
        for attempt in range(5):
            reqdata = {'client_id': self.__client_id,
                       'device_code': self.__device_code,
                       'grant_type': 'urn:ietf:params:oauth:grant-type:device_code'}
            req = urllib2.Request('https://github.com/login/oauth/access_token', data=json.dumps(reqdata), headers=self.__headers)
            req.get_method = lambda: 'POST'
            code, ret = urlopen_nt(req)
            if code == 200:
                rep = json.loads(ret.read())
                if 'error' not in rep:
                    self.__result = rep
                    break

                errcode = rep['error']
                if errcode == 'authorization_pending':
                    time.sleep(self.__interval)
                    continue
                elif errcode == 'slow_down':
                    self.__interval = rep.get('interval', self.__interval + 5)
                    time.sleep(self.__interval)
                    continue
                elif errcode == 'expired_token':
                    # TODO: alert user, restart the process
                    raise NotImplementedError()
                elif errcode == 'unsupported_grant_type':
                    raise RuntimeError('unsupported grant type. probably github changed API. need to update the plugin')
                elif errcode == 'incorrect_client_credentials':
                    raise RuntimeError('incorect client id. probably pedohorse changed hpaste id for some reason. update the plugin')
                elif errcode == 'incorrect_device_code':
                    # TODO: alert user, restart the process
                    raise NotImplementedError()
                elif errcode == 'access_denied':
                    # means user denied the request
                    self.__result = None
                else:
                    raise RuntimeError('unexpected error: %s' % (json.dumps(rep),))
            else:
                raise NotImplementedError()
        else:
            raise NotImplementedError()

        return super(QGithubDeviceAuthDialog, self).closeEvent(event)

    def on_url_changed(self, qurl):
        url = qurl.toString()
        print(url)


if __name__ == '__main__':  # testing
    import sys
    import string
    import random
    from PySide2.QtWidgets import QApplication
    qapp = QApplication(sys.argv)
    # w = QWebAuthDialog('https://www.google.com', r'https://www.google.com/search\?(.*)')
    webauthstate = ''.join(random.choice(string.ascii_letters) for _ in xrange(32))
    webauthparms = {'client_id': '42e8e8e9d844e45c2d05',
                    'redirect_uri': 'https://github.com/login/oauth/success',
                    'scope': 'gist',
                    'state': webauthstate}
    w = QGithubDeviceAuthDialog(client_id='42e8e8e9d844e45c2d05', parent=None)
    w.setGeometry(512, 256, 1024, 768)
    res = w.exec_()
    print(res == QGithubDeviceAuthDialog.Accepted)
    print(w.get_result())

