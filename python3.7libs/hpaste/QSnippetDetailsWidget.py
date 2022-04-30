# it's high time to forget Qt4, this will be qt5 only
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit, QCheckBox, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy
from PySide2.QtCore import Slot, Qt, QSize
from .hpasteweb import webUnpack
from .hpaste import stringToData

from typing import Optional


class QSnippetDetailsWidget_ui:
    def add_text_view(self, wgt: QWidget, label: str):
        if isinstance(wgt, QLineEdit):
            wgt.setReadOnly(True)
        lbl = QLabel(label)
        self._labels.append(lbl)
        self.data_layout.addWidget(lbl, self.__data_lay_row, 0)
        self.data_layout.addWidget(wgt, self.__data_lay_row, 1)
        self.__data_lay_row += 1

    def __init__(self, parent: QWidget):
        self.__data_lay_row = 0
        self.main_layout = QVBoxLayout()
        parent.setLayout(self.main_layout)

        self.snippet_input = QLineEdit()
        self.snippet_input.setPlaceholderText('put snippet link here')

        self.is_encrypted = QCheckBox('encrypted')
        self.is_encrypted.setEnabled(False)

        self.is_singed = QCheckBox('signed')
        self.is_singed.setEnabled(False)

        self.data_layout = QGridLayout()
        data_lay_row = 0
        self._labels = []



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
        self.hdalist.horizontalHeader().setStretchLastSection(True)
        self.hdalist.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.hdalist.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.hdalist.horizontalHeader().setVisible(False)
        self.hdalist.verticalHeader().setVisible(False)
        self.hdalist.setSizeAdjustPolicy(QTableWidget.AdjustToContents)
        self.hdalist.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)

        self.hpformat= QLineEdit()
        self.add_text_view(self.hpformat, 'snippet format')

        self.main_layout.addWidget(self.snippet_input)
        self.main_layout.addWidget(self.is_encrypted)
        self.main_layout.addLayout(self.data_layout)


class QSnippetDetailsWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super(QSnippetDetailsWidget, self).__init__(parent)
        self.ui = QSnippetDetailsWidget_ui(self)
        self.__last_snippet = ''
        self.setMinimumWidth(400)

        # connec
        self.ui.snippet_input.editingFinished.connect(self.fill_information)

        self.adjustSize()

    @Slot()
    def fill_information(self):
        url = self.ui.snippet_input.text().strip()
        if self.__last_snippet == url:
            return
        self.__last_snippet = url
        snippet = webUnpack(url)
        data, deserializer = stringToData(snippet)

        self.ui.is_encrypted.setEnabled(data.get('encrypted', False))
        self.ui.is_singed.setEnabled(data.get('signed', False))
        self.ui.chsum.setText(data.get('chsum', '<N/A>'))
        self.ui.context.setText(data.get('context', '<N/A>'))
        self.ui.houver.setText('.'.join(str(x) for x in data['houver']) if 'houver' in data else '<N/A>')
        self.ui.author.setText(data.get('author', '<N/A>'))
        self.ui.hpformat.setText(str(data.get('version', 0)) + ('.{}'.format(data['version.minor']) if 'version.minor' in data else ''))
        self.ui.datasize.setText(nice_memory_formatting(len(data.get('code', ''))))

        hda_list = data.get('hdaList', [])
        if hda_list:
            self.ui.hdalist.setColumnCount(3)
            self.ui.hdalist.setRowCount(len(hda_list))
            for i, item in enumerate(hda_list):
                self._update_hda_item(nice_memory_formatting(len(item.get('code', ''))), i, 0)
                self._update_hda_item(item.get('category', '<N/A>'), i, 1)
                self._update_hda_item(item.get('type', '<N/A>'), i, 2)

        self.adjustSize()
        from pprint import pprint
        pprint(data)

    def _update_hda_item(self, text, row, col):
        item = self.ui.hdalist.item(row, col)
        if item is None:
            item = QTableWidgetItem(text)
            self.ui.hdalist.setItem(row, col, item)
        item.setText(text)


def nice_memory_formatting(memory_bytes: int) -> str:
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

    sys.exit(qapp.exec_())


if __name__ == '__main__':
    test()
