import numpy
import re
from lib.util import Util
from lib.words import Words

class Cheng:
    def __init__(self, users, tweets, lwords):
        self.users = users
        self.user_distributions = {}
        self.tweets = tweets
        self.lwords = lwords # local words if extracted in advance

    def extract_local_words_batch(self, params):
        lwords = {}
        word_counts = {}

        for user in self.users.iter():
            location = user['location_point']
            if location != None:
                tweets = self.tweets.get(user['id'])
                user_words = set([])
                city = str(tuple(location))
                for tweet in tweets:
                    user_words |= set(Util.get_nouns(tweet['text'], params['lang']))
                for w in user_words:
                    if not w in word_counts:
                        word_counts[w] = {city: 1}
                    elif not city in word_counts[w]:
                        word_counts[w][city] = 1
                    else:
                        word_counts[w][city] += 1

        """ calculating divergences """
        for w in word_counts:
            N = float(sum([v for v in word_counts[w].values()]))
            if N >= params['cmin']:
                d = self.calc_dispersion(word_counts[w], params)
                if d < params['dmax']:
                        lwords[w] = {'word':w, 'd':d, 'distribution':word_counts[w]} # save as dict
        return Words(lwords)

    def calc_dispersion(self, word_count, params):
        points = [self.str_to_tuple(k) for k,v in word_count.items() for i in range(0, v)]
        d = Util.calc_dispersion(points)
        return d

    def update_user_distributions(self, tweet, params):
        user = self.users.get(tweet['user_id'])
        if user != None:
            if user['location_point'] == None:
                """ unlabeled users """
                if not user['id'] in self.user_distributions:
                    self.user_distributions[user['id']] = self.init_user_distribution()
                words = Util.get_nouns(tweet['text'], params['lang'])
                for w in words:
                    if self.lwords.contain(w):
                        """ update using local word """
                        lword = self.lwords.get(w)
                        if lword['d'] < params['dmax']:
                            self.user_distributions[user['id']] = self.add_distribution(self.user_distributions[user['id']], lword['distribution'])

    def add_distribution(self, p, q):
        for k in q:
            if not k in p: p[k] = 0
            p[k] += q[k]
        return p

    def init_user_distribution(self):
        return {}

    def predict(self, user_distribution, params):
        max_p = 0
        max_city = None
        for k, v in user_distribution.items():
            if v > max_p:
                max_p = v
                max_city = k
        return max_city

    def infer(self, params):
        window = {'tweets':[], 'start':0} # storing tweets

        """ User distribution updating """
        for tweet in self.tweets.stream():
            if type(tweet) == type({}):
                self.update_user_distributions(tweet, params)

        """ Location prediction using user distribution """
        for user in self.users.iter():
            if user['location_point'] == None:
                """ unlabeled user """
                if user['id'] in self.user_distributions and len(self.user_distributions[user['id']]) > 0:
                    inferred_city = self.predict(self.user_distributions[user['id']], params)
                    inferred_location = Util.str_to_tuple(inferred_city)
                    user['location_point'] = inferred_location

    def get_users(self):
        return self.users

if __name__ == '__main__':
    import sys
    from lib.db import DB
    from lib.users import Users
    from lib.tweets_db import Tweets
    from lib.words import Words

    if len(sys.argv) < 5:
        print '[usage]: python %s [users file path] [db user name] [db pass] [db name]' % sys.argv[0]
        exit()

    users = Users()
    users.load_file(sys.argv[1])
    db = DB(sys.argv[2], sys.argv[3], sys.argv[4])
    tweets = Tweets(db)
    lwords = Words()

    ch = Cheng(users, tweets, lwords)
    #print tl.extract_local_words({'dmin':0.05, 'cmin':30})
    #print tl.extract_local_words_(tl.tweets.stream(), {'dmin':0.05, 'cmin':30, 'window_size':1800, 'tl':False, 'default':False, 'divergence':'l2'})
    print ch.extract_local_words_batch({'dmax':400000, 'cmin':30, 'lang': 'en'})
    #print tl.extract_local_words_batch({'dmin':1.0, 'cmin':30, 'window_size':1800, 'tl':False, 'default':False, 'divergence':'kl'})
    #print tl.extract_local_words_batch({'dmin':300000, 'cmin':30, 'window_size':1800, 'tl':False, 'default':False, 'divergence':'dispersion'})

