# -*- coding: utf-8 -*-

import MySQLdb
from low_level_cursor import LowLevelCursor

class DB:
    def __init__(self, user, passwd, db, host='localhost'):
        self.connect = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db)
        self.connect.cursorclass = MySQLdb.cursors.DictCursor
        self.cursor = self.connect.cursor()
        self.issue_insert('set names utf8')

    def issue_select(self, query):
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except MySQLdb.Error, e:
            return e

    def iter_select(self, query, n=100):
        try:
            self.connect.ping(True)
            low_level_cursor = LowLevelCursor(self.connect, n)
            low_level_cursor.query(query)
            if n == 1:
                for row in low_level_cursor:
                    yield row
            else:
                for rows in low_level_cursor:
                    for row in rows:
                        yield row

        except MySQLdb.Error, e:
            yield e

    def issue_insert(self, query):
        try:
            self.cursor.execute(query)
            self.connect.commit()
        except MySQLdb.Error, e:
            # Duplicate entry
            if e[0] == 1062:
                pass
            else:
                return e

if __name__ == '__main__':
    import sys
    db = DB(sys.argv[1], sys.argv[2], sys.argv[3])
    for row in db.iter_select('select text from tweets limit 100000'):
        100 + 100
