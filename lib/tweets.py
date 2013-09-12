import json
from util import Util

class Tweets:
    def __init__(self):
        self.values = {}

    def __str__(self):
        res = ""
        for user_id in self.values:
            for tweet in self.values[user_id]:
                res += json.dumps(tweet) + "\n"
        return res[:-1]

    def load_file(self, filepath):
        for line in open(filepath, 'r'):
            tweet = json.loads(line.rstrip())
            if not tweet['user_id'] in self.values: self.values[tweet['user_id']] = []
            self.values[tweet['user_id']].append(tweet)
 
    def load_mysql(self, mysqldb, users):
        for user in users.iter():
            query = "SELECT id, text, user_id, timestamp FROM tweets WHERE user_id = %s ORDER BY id DESC LIMIT 200" % user['id']
            result = mysqldb.issue_select(query)
            if type(result) == type(()):
                tweets = []
                for row in result:
                    row['timestamp'] = Util.time_to_str(row['timestamp'])
                    tweets.append(row)
                self.values[user['id']] = tweets

    def load_mongodb(self, mongodb):
        pass
    
    def get(self, user_id):
        """ get tweets posted by user_id """
        if user_id in self.values:
            return self.values[user_id]
        else:
            return None

    def user_iter(self):
        for user_id in self.values:
            yield user_id

    def iter(self):
        for user_id in self.values:
            for tweet in self.values[user_id]:
                yield tweet

    def stream(self):
        tweets = {}
        for user_id in self.values:
            for tweet in self.values[user_id]:
                tweets[tweet['id']] = tweet
        for tid in sorted(tweets):
            yield tweets[tid]


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print '[usage]: python %s [tweets filepath]' % sys.argv[0]
        exit()

    tweets = Tweets()
    tweets.load_file(sys.argv[1])
