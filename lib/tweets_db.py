import json
from util import Util

class Tweets:
    def __init__(self, db):
        self.db = db

    def get(self, user_id):
        """ get tweets posted by user_id """
        query = "SELECT id, text, timestamp, user_id FROM tweets WHERE user_id = %s ORDER BY id DESC LIMIT 200" % user_id
        result = self.db.issue_select(query)
        if type(result) == type(()):
            return result
        else:
            return ()

    def stream(self):
        query = "SELECT id, text, timestamp, user_id FROM tweets ORDER BY id"
        for row in self.db.iter_select(query):
            yield row

    def iter(self):
        query = "SELECT id, text, timestamp, user_id FROM tweets"
        for row in self.db.iter_select(query):
            yield row


if __name__ == '__main__':
    import sys
    from db import DB

    if len(sys.argv) < 4:
        print '[usage]: python %s [db user name] [db pass] [db name]' % sys.argv[0]
        exit()

    db = DB(sys.argv[1], sys.argv[2], sys.argv[3])
    tweets = Tweets(db)
    for t in tweets.stream():
        print t
