# it's high time to forget Qt4, this will be qt5 only
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit, QCheckBox,\
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy, QMessageBox, QDialog, QTextEdit, QPushButton
from PySide2.QtCore import Slot, Qt, QSize
from .hpasteweb import webUnpack
from .hpaste import stringToData, WrongKeyError
from .codeanalysis import generate_report_data

try:
    from typing import Optional
except ImportError:  # for py2
    pass


class QSnippetDetailsWidget_ui:
    def add_text_view(self, wgt, label):
        # type: (QWidget, str) -> None
        if isinstance(wgt, QLineEdit):
            wgt.setReadOnly(True)
        lbl = QLabel(label)
        self._labels.append(lbl)
        self.data_layout.addWidget(lbl, self.__data_lay_row, 0)
        self.data_layout.addWidget(wgt, self.__data_lay_row, 1)
        self.__data_lay_row += 1

    def __init__(self, parent):
        # type: (QWidget) -> None
        self.__data_lay_row = 0
        self.main_layout = QVBoxLayout()
        parent.setLayout(self.main_layout)

        self.data_layout = QGridLayout()
        self._labels = []

        self.snippet_input = QLineEdit()
        self.snippet_input.setPlaceholderText('put snippet link here')

        self.is_encrypted = QCheckBox('encrypted')
        self.is_encrypted.setEnabled(False)
        self.add_text_view(self.is_encrypted, 'encryption')

        self.is_singed = QCheckBox('signed')
        self.is_singed.setEnabled(False)
        self.add_text_view(self.is_singed, 'signature')

        self.chsum = QLineEdit()
        self.add_text_view(self.chsum, 'checksum')

        self.context = QLineEdit()
        self.add_text_view(self.context, 'context')

        self.houver = QLineEdit()
        self.add_text_view(self.houver, 'houdini')

        self.author = QLineEdit()
        self.add_text_view(self.author, 'author')

        self.datasize = QLineEdit()
        self.add_text_view(self.datasize, 'data size')

        self.hdalist = QTableWidget()
        self.add_text_view(self.hdalist, 'embedded HDAs')
        self.hdalist.setColumnCount(3)
        # self.hdalist.horizontalHeader().setStretchLastSection(True)
        self.hdalist.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.hdalist.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.hdalist.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.hdalist.horizontalHeader().setVisible(False)
        self.hdalist.verticalHeader().setVisible(False)
        self.hdalist.setSizeAdjustPolicy(QTableWidget.AdjustToContents)
        self.hdalist.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)

        self.details_button = QPushButton('show details')
        self.details_button.setEnabled(False)
        self.add_text_view(self.details_button, 'code analysis')

        self.hpformat = QLineEdit()
        self.add_text_view(self.hpformat, 'snippet format')

        self.main_layout.addWidget(self.snippet_input)
        self.main_layout.addLayout(self.data_layout)


class QSnippetDetailsWidget(QWidget):
    def __init__(self, parent=None):
        # type: (Optional[QWidget]) -> None
        super(QSnippetDetailsWidget, self).__init__(parent)
        self.setWindowTitle('snippet inspector')
        self.setWindowFlag(Qt.Dialog)
        self.setProperty('houdiniStyle', True)
        self.ui = QSnippetDetailsWidget_ui(self)
        self.setMinimumWidth(400)
        self.__last_snippet = ''
        self.__last_snippet_code = None

        # connec
        self.ui.snippet_input.editingFinished.connect(self.fill_information)
        self.ui.details_button.pressed.connect(self.show_code_details)

        self.adjustSize()

    def show_code_details(self):
        if self.__last_snippet_code is None:
            return
        wgt = QDetailsDialog(self.__last_snippet_code[0], self.__last_snippet_code[1], self)
        wgt.finished.connect(wgt.deleteLater)
        wgt.show()

    def _clear_info(self):
        self.ui.is_encrypted.setChecked(False)
        self.ui.is_singed.setChecked(False)
        self.ui.chsum.setText('')
        self.ui.context.setText('')
        self.ui.houver.setText('')
        self.ui.author.setText('')
        self.ui.hpformat.setText('')
        self.ui.datasize.setText('')
        self.ui.hdalist.setRowCount(0)
        self.ui.details_button.setEnabled(False)
        self.__last_snippet_code = None
        self.__last_snippet = ''
        self.adjustSize()

    @Slot()
    def fill_information(self):
        url = self.ui.snippet_input.text().strip()
        if self.__last_snippet == url:
            return
        self.__last_snippet = url

        key = None
        if '!' in url:
            key, url = url.split('!', 1)

        try:
            snippet = webUnpack(url)
        except RuntimeError as e:
            QMessageBox.warning(self, 'error retrieving the snippet', str(e))
            self._clear_info()
            return
        self.__last_snippet_code = (snippet, key)
        try:
            data, _ = stringToData(snippet, key)
        except Exception as e:
            QMessageBox.warning(self, 'error parsing the snippet', str(e))
            self._clear_info()
            return

        code = data.get('code', '')
        self.ui.is_encrypted.setChecked(data.get('encrypted', False))
        self.ui.is_singed.setChecked(data.get('signed', False))
        self.ui.chsum.setText(data.get('chsum', '<N/A>'))
        self.ui.context.setText(data.get('context', '<N/A>'))
        self.ui.houver.setText('.'.join(str(x) for x in data['houver']) if 'houver' in data else '<N/A>')
        self.ui.author.setText(data.get('author', '<N/A>'))
        self.ui.hpformat.setText(str(data.get('version', 0)) + ('.{}'.format(data['version.minor']) if 'version.minor' in data else ''))
        self.ui.datasize.setText(nice_memory_formatting(len(code)))

        hda_list = data.get('hdaList', [])
        if hda_list:
            self.ui.hdalist.setColumnCount(3)
            self.ui.hdalist.setRowCount(len(hda_list))
            for i, item in enumerate(hda_list):
                self._update_hda_item(nice_memory_formatting(len(item.get('code', ''))), i, 0)
                self._update_hda_item(item.get('category', '<N/A>'), i, 1)
                self._update_hda_item(item.get('type', '<N/A>'), i, 2)

        self.ui.details_button.setEnabled(True)

        self.adjustSize()

    def _update_hda_item(self, text, row, col):
        item = self.ui.hdalist.item(row, col)
        if item is None:
            item = QTableWidgetItem(text)
            self.ui.hdalist.setItem(row, col, item)
        item.setText(text)


class QDetailsDialog(QDialog):
    def __init__(self, snippet, key=None, parent=None):
        super(QDetailsDialog, self).__init__(parent)
        self.setModal(True)

        self.__main_layout = QVBoxLayout()
        self.setLayout(self.__main_layout)

        self.__warning = QLabel('Warning! hip(nl/lc) is a proprietary format\n'
                                'Everything below is gained through surface pattern analysis, not proper structural analysis\n'
                                'So information may be not 100% correct!')
        self.__main_layout.addWidget(self.__warning)

        self.__info_detail = QTextEdit()
        self.__info_detail.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.__info_detail.setReadOnly(True)
        self.__main_layout.addWidget(self.__info_detail)

        self.set_data(snippet, key)

    def set_data(self, snippet, ekey):
        # type: (str, str) -> None
        text_parts = []
        try:
            data = generate_report_data(snippet, ekey)
        except WrongKeyError:
            self.__info_detail.setText('data encrypted, no valid key provided')
            return
        for key in sorted(data.keys()):
            val = data[key]
            if isinstance(val, str):
                text_parts += ['{}: {}'.format(key, val)]
            elif isinstance(val, (set, list, tuple)):
                if len(val) == 0:
                    text_parts += ['{}:'.format(key)]
                    continue
                if isinstance(val, set):  # for uniformity
                    val = list(val)
                if isinstance(val[0], (str, bytes)):
                    sorted_val = sorted(val)
                elif isinstance(val[0], tuple):
                    # assume all tuples are same length
                    toffsets = [max(len(x[i]) for x in val) + 2 for i in range(len(val[0]))]
                    sorted_val = sorted(''.join('{{:{}s}}'.format(off).format(x) for off, x in zip(toffsets, val_i)) for val_i in val)
                else:
                    sorted_val = sorted(str(x) for x in val)
                offset = len(key) + 2
                text_parts += ['{}: '.format(key) + ('\n' + ' '*offset).join(str(x) for x in sorted_val)]

        self.__info_detail.setText('<pre>' + '\n\n'.join(text_parts) + '</pre>')
        self.adjustSize()


def nice_memory_formatting(memory_bytes):
    # type: (int) -> str
    suff = ('B', 'KB', 'MB', 'GB', 'TB', 'PB')
    next_suff = 'EB'
    for su in suff:
        if memory_bytes < 1100:
            return '{memory_bytes}{su}'.format(memory_bytes=memory_bytes,
                                               su=su)
        memory_bytes //= 1000
    return '{memory_bytes}{next_suff}'.format(memory_bytes=memory_bytes,
                                              next_suff=next_suff)


def test():
    import sys
    from PySide2.QtWidgets import QApplication
    qapp = QApplication(sys.argv)

    wgt = QSnippetDetailsWidget()
    wgt.show()
    # uyoduviriw@HPaste
    # darehetiwu@HPaste
    # dXrQZpY6glXBpinc!atolayiwel@HPaste

    sys.exit(qapp.exec_())


if __name__ == '__main__':
    test()
