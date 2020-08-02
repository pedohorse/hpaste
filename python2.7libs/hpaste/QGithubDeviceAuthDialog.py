import re
import json
import urllib2
from nethelper import urlopen_nt
try:
    from PySide2.QtWidgets import QDialog, QVBoxLayout, QLabel
    from PySide2.QtWebEngineWidgets import QWebEngineView
    from PySide2.QtCore import QUrl
except ImportError:
    raise NotImplementedError('web auth implemented only for QT5. Sorry, people who still use houdini 16.5')


class QGithubDeviceAuthDialog(QDialog):
    def __init__(self, client_id, parent=None):
        super(QGithubDeviceAuthDialog, self).__init__(parent=parent)

        self.__webview = QWebEngineView(parent=self)
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
        reqdata = {'client_id': self.__client_id, 'scope': 'gist'}
        req = urllib2.Request('https://github.com/login/device/code', data=json.dumps(reqdata), headers={'User-Agent': 'HPaste', 'Accept': 'application/json'})
        req.get_method = lambda: 'POST'
        code, ret = urlopen_nt(req)
        if code != 200:
            raise RuntimeError('code %d when trying to register device' % code)
        init_data = json.loads(ret.read())
        print(init_data)
        self.__webview.load(QUrl(init_data['verification_uri']))
        self.__devidlabel.setText(init_data['user_code'])

    def get_result(self):
        return self.__result

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
    if res == QGithubDeviceAuthDialog.Accepted:
        print w.get_result().groups()
    # qapp.exec_()
