#
# This is a simple example of a plugin that stores code on local server to allow
# exchanging of short snippets while with code not leaving company's subnetwork
#
from __future__ import print_function, absolute_import
import os
import random
import string
import time
import sqlite3

from ..webclipboardbase import WebClipBoardBase, WebClipBoardWidNotFound
from .. import hpasteoptions as opt


# rename this class adequate to your net, this name will be the plugin name
# that goes after @ in qYUs2jkq@LocalSQLite link
class LocalSQLite(WebClipBoardBase):
    def __init__(self):
        # in this example all snippets will be stored in separate sqlite database
        # on your local network, accessible to everyone.
        # autocleaning is done with a trigger
        # this example can be easily adapted to use with any other sql-based database
        # butt beware - single multiuser access to sqlite over unreliable network may result in database locking
        self.__databasePath = r'/tmp/some/network/path/to/mysql.db'

        # and this is just a set of allowed symbols we use.
        # you can limit this set however you want, but if you want to extend it -
        # be sure NOT to use symbols @ # ! and honestly - better keep it ascii
        self.__symbols = string.ascii_lowercase + string.ascii_uppercase + string.ascii_letters
        self.__expiration_interval = 1 * 365 * 24 * 60 * 60  # one year

    def initDb(self):
        dirname = os.path.dirname(self.__databasePath)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        if not os.path.exists(self.__databasePath):
            with sqlite3.connect(self.__databasePath) as con:
                con.execute('CREATE TABLE IF NOT EXISTS "entries" ('
                            '"id" TEXT NOT NULL PRIMARY KEY,'
                            '"created_at" INT,'
                            '"last_accessed_at" INT,'
                            '"expires_at" INT,'
                            '"data" TEXT'
                            ')')
                con.execute('CREATE TRIGGER IF NOT EXISTS "delete_expired" '
                            'AFTER INSERT '
                            'ON "entries" '
                            'BEGIN '
                            'DELETE FROM entries WHERE expires_at < strftime("%s", "now");'
                            'END;')
                con.commit()

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
        # since we use sqlite db to store them in this example
        return 10 ** 20

    def webPackData(self, s):  # type: (str) -> str
        """
        override this from WebClipBoardBase
        this takes in a big string of data, already guaranteed url-safe
        and should do something to associate and return some short id with that data.
        it doesn't matter how id looks like, but it is advised to heve it url-safe as well
        """
        self.initDb()

        wid_size = 12
        assert len(s) <= self.maxStringLength()  # this is actually guaranteed by the caller
        try:
            with sqlite3.connect(self.__databasePath) as con:
                con.execute('BEGIN')
                # start transaction and generate wid in an uninterrupted way
                for attempt in range(8):  # highly improbably that we will need more than 1 attempt
                    wid = ''.join(random.choice(self.__symbols) for _ in range(wid_size))
                    cur = con.cursor()
                    cur.execute('SELECT COUNT("id") FROM "entries" WHERE "id" == ?', (wid,))
                    res = cur.fetchone()[0]
                    if res == 0:
                        break
                else:
                    con.rollback()
                    raise RuntimeError('could not generate unique wid!')
                timestamp = int(time.time())
                con.execute('INSERT INTO "entries" ("id", "created_at", "last_accessed_at", "expires_at", "data") '
                            'VALUES (?, ?, ?, ?, ?)', (wid, timestamp, timestamp, timestamp + self.__expiration_interval, s))
                con.commit()
        except Exception as e:
            raise RuntimeError("error writing to local server: " + str(e))

        return wid

    def webUnpackData(self, wid):
        """
        given proper wid, one previously generated by webPackData,
        return the snippet associated with that wid
        """
        try:
            with sqlite3.connect(self.__databasePath) as con:
                cur = con.cursor()
                cur.execute('SELECT "data" FROM "entries" WHERE "id" = ?', (wid,))
                s = cur.fetchone()
                if s is None:
                    raise WebClipBoardWidNotFound(wid)
                s = s[0]
                timestamp = int(time.time())
                con.execute('UPDATE "entries" SET "last_accessed_at" = ?, "expires_at" = ?',
                            (timestamp, timestamp + self.__expiration_interval))
        except Exception as e:
            raise RuntimeError("error reading from local server: " + str(e))

        return s
