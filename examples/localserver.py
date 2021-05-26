#
# This is a simple example of a plugin that stores code on local server to allow
# exchanging of short snippets while with code not leaving company's subnetwork
#
from __future__ import print_function, absolute_import
import os
import random
import string

from ..webclipboardbase import WebClipBoardBase, WebClipBoardWidNotFound
from .. import hpasteoptions as opt


# rename this class adequate to your net, this name will be the plugin name
# that goes after @ in qYUs2jkq@LocalServer link
class LocalServer(WebClipBoardBase):
    def __init__(self):
        # in this example all snippets will be stored in separate files in some dir
        # on your local network, accessible to everyone.
        # There is no autocleaning feature here
        self.__basePath = r'/tmp/some/self/cleaning/dir'
        self.__symbols = string.ascii_lowercase + string.ascii_uppercase + string.ascii_letters

    @classmethod
    def speedClass(cls):
        """
        returns int, speed class of your plugin.
        returned int value will be used for initial plugin sort.
        this makes more sense for internet plugins,
        for local ones like this one you can just put a big number here
        """
        return opt.getOption('hpasteweb.plugins.%s.speed_class' % cls.__name__, 11)

    @classmethod
    def maxStringLength(cls):
        """
        returns maximum size of one entry.
        in case incoming snippet is bigger than this - it will be automatically
        splitted into parts fitting maxStringLength() value
        and user will get a longer snippet link like 12345678@LocalServer#23456789@LocalServer...
        """
        # we return 10 MiB, but there is actually no point limiting snippet
        # since we use files to store them in this example
        return 10**20

    def genId(self, size=12):
        """
        generates id to be used in the link.
        you are free to embed user id, hostname or whatever you want in it
        """
        if size < 1 or size > 4096:
            raise RuntimeError("improper size")

        lsmo = len(self.__symbols) - 1
        for attempt in range(8):  # highly improbably that we will need more than 1 attempt
            wid = ''.join(random.choice(self.__symbols) for _ in range(size))
            if not os.path.exists(os.path.join(self.__basePath, wid)):
                break
        else:
            raise RuntimeError('could not generate unique wid!')
        return wid

    def webPackData(self, s):  # type: (str) -> str
        """
        override this from WebClipBoardBase
        this takes in a big string of data, already guaranteed url-safe
        and should do something to associate and return some short id with that data.
        it doesn't matter how id looks like, but it is advised to heve it url-safe as well
        """
        if not os.path.exists(self.__basePath):
            os.makedirs(self.__basePath)
        wid = self.genId()
        assert len(s) <= self.maxStringLength()  # this is actually guaranteed by the caller
        try:
            with open(os.path.join(self.__basePath, wid), 'w') as f:
                f.write(s)
        except Exception as e:
            raise RuntimeError("error writing to local server: " + str(e))

        return wid

    def webUnpackData(self, wid):
        """
        given proper wid, one previously generated by webPackData,
        return the snippet associated with that wid
        """
        try:
            widpath = os.path.join(self.__basePath, wid)
            if not os.path.exists(widpath):
                raise WebClipBoardWidNotFound(wid)
            with open(widpath) as f:
                s = f.read()
        except Exception as e:
            raise RuntimeError("error reading from local server: " + str(e))

        return s
