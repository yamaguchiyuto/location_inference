# -*- coding: utf-8 -*-

import MySQLdb

def get_connection(connect_info):
    return MySQLdb.connect(**connect_info)

class LowLevelCursor(object):
    def __init__(self, connection, rows=1, value_type=1):
        self.connection = connection
        self.rows = rows
        self.value_type = value_type
        self.rs = None
        self.row = None
    
    def query(self, sql):
        self.connection.query(sql)
        self.rs = self.connection.use_result()
    
    def has_next(self):
        self.row = self.rs.fetch_row(self.rows, self.value_type)
        return bool(self.row)
    
    def next(self):
        return self.row[0] if self.rows == 1 else self.row
    
    def __iter__(self):
        while(self.has_next()):
            yield self.next()

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 4:
        print '[usage]: python %s [db user name][db pass][db name]' % sys.argv[0]
        exit()

    foo = {
        'db' : sys.argv[3],
        'host' : "127.0.0.1",
        'port' : 3306,
        'user' : sys.argv[1],
        'passwd' : sys.argv[2]
    }
    
    connection = get_connection(foo)
    cursor = LowLevelCursor(connection)
    cursor.query('select * from tweets order by id')
    for i in cursor:
        print i
