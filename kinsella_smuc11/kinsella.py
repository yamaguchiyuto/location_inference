import math
from lib.util import Util

class Kinsella:
    def __init__(self, users, tweets, model=None):
        self.users = users
        self.tweets = tweets
        self.model = model

    def learn(self, params):
        tf = {} # term frequency in a location
        lf = {} # location frequency
        global_tf = {} # term frequency
        all_tf = 0.0

        for user in self.users.iter():
            location = user['location_point']
            if location != None:
                tweets = self.tweets.get(user['id'])
                user_words = set([])
                location = tuple(location)

                if not location in tf: tf[location] = {}
                if not location in lf: lf[location] = 0

                for tweet in tweets:
                    user_words |= set(Util.get_nouns(tweet['text'], params['lang']))

                for w in user_words:
                    if not w in tf[location]: tf[location][w] = 0
                    if not w in global_tf: global_tf[w] = 0
                    tf[location][w] += 1
                    global_tf[w] += 1
                    lf[location] += 1
                    all_tf += 1

        for w in global_tf.keys():
            if global_tf[w] < params['mincount']:
                del global_tf[w]
            else:
                global_tf[w] /= all_tf

        return {'tf':tf, 'global_tf':global_tf, 'lf':lf}
    
    def term_likelihood(self, term, location, params):
        if term in self.model['global_tf']:
            if term in self.model['tf'][location]:
                li = math.log((self.model['tf'][location][term] + params['mu'] * self.model['global_tf'][term]) / float(self.model['lf'][location] + params['mu']))
            else:
                li = math.log((params['mu'] * self.model['global_tf'][term]) / float(self.model['lf'][location] + params['mu']))
            return li
        else:
            return 0
    
    def tweet_likelihood(self, terms, location, params):
        li = 0
        for term in terms:
            li += self.term_likelihood(term, location, params)
        return li


    def infer_one(self, user_id, params):
        tweets = self.tweets.get(user_id)
        user_words = set([])
        for tweet in tweets:
            user_words |= set(Util.get_nouns(tweet['text'], params['lang']))

        max_location = None
        max_likelihood = -10000000000
        for location in self.model['lf']:
            likelihood = self.tweet_likelihood(user_words, location, params)
            if max_likelihood < likelihood:
                max_likelihood = likelihood
                max_location = location
        return max_location

    def infer(self, params):
        for user in self.users.iter():
            if user['location_point'] == None:
                user['location_point'] = self.infer_one(user['id'], params)

    def get_users(self):
        return self.users


if __name__ == '__main__':
    import sys
    import pickle
    from lib.db import DB
    from lib.users import Users
    from lib.tweets_db import Tweets

    if len(sys.argv) < 3:
        print '[usage]: python %s [users file path] [db user name] [db pass] [db name]' % sys.argv[0]
        exit()
    
    users = Users()
    users.load_file(sys.argv[1])
    db = DB(sys.argv[2], sys.argv[3], sys.argv[4])
    tweets = Tweets(db)

    method = Kinsella(users, tweets)
    model = method.learn({'lang':'ja', 'mincount':30})

    f = open('kinsella.model', 'w')
    pickle.dump(model, f)
    f.close()
