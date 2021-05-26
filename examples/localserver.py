#
# This is a simple example of a plugin that stores code on local server to allow
# exchanging of short snippets while with code not leaving company's subnetwork
#
from __future__ import print_function, absolute_import
import os
import random

from ..webclipboardbase import WebClipBoardBase
from .. import hpasteoptions as opt


class LocalServer(WebClipBoardBase):
    def __init__(self):
        # in simple case - you can just put here your local temp path, and everything else should work by itself
        self.__basePath = r'/tmp/some/self/cleaning/dir'

    @classmethod
    def speedClass(cls):
        return opt.getOption('hpasteweb.plugins.%s.speed_class' % cls.__name__, 10)

    @classmethod
    def maxStringLength(cls):
        return 10**20

    def genId(self, size=8):
        """
        generates id to be used in the link.
        you are free to embed user id, hostname or whatever you want in it
        """
        if size < 1 or size > 4096:
            raise RuntimeError("improper size")

        lsmo = len(self.__symbols) - 1
        for attempt in range(8):  # highly improbably that we will need more than 1 attempt
            wid = ''
            for i in range(size):
                wid += self.__symbols[random.randint(0, lsmo)]
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
        wid = self.genId()
        assert len(s) <= self.maxStringLength()  # this is actually guaranteed by the caller
        try:
            with open(os.path.join(self.__basePath, wid)) as f:
                f.write(s)
        except Exception as e:
            raise RuntimeError("error writing to local server: " + str(e))

        return wid

    def webUnpackData(self, wid):

        try:
            with open(os.path.join(self.__basePath, wid)) as f:
                s = f.read()
        except Exception as e:
            raise RuntimeError("error reading from local server: " + str(e))

        return s
