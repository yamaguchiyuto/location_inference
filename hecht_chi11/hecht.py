from lib.util import Util

class Hecht:
    def __init__(self, users, tweets, model=None):
        self.users = users
        self.tweets = tweets
        self.model = model

    def calgari(self, params):
        all_tf = 0.0
        tf = {}
        calgari_value = {}
        pc = {}
        pwc = {}

        for user in self.users.iter():
            location = user['location_point']
            if location != None:
                tweets = self.tweets.get(user['id'])
                user_words = set([])
                city = str(tuple(location))

                if not city in pc: pc[city] = 0
                pc[city] += 1

                for tweet in tweets:
                    user_words |= set(Util.get_nouns(tweet['text'], params['lang']))
                for w in user_words:
                    if not w in pwc:
                        pwc[w] = {city: 1}
                        tf[w] = 0.0
                    elif not city in pwc[w]:
                        pwc[w][city] = 1
                    else:
                        pwc[w][city] += 1
                    all_tf += 1
                    tf[w] += 1

        """ calculating calgari value """
        for w in tf:
            if tf[w] < params['minu']:
                del pwc[w]
            else:
                max_prob = max(pwc[w].values())
                calgari_value[w] = (max_prob / tf[w]) / (tf[w] / all_tf)

        """ building model """
        count = 0
        for w, v in sorted(calgari_value.items(), key=lambda x:x[1], reverse=True):
            count += 1
            if count > params['max_count']:
                if w in pwc: del pwc[w]

        return {'pc':pc, 'pwc':pwc}

    def set_model(self, model):
        self.model = model

    def model_dump(self):
        for w in self.model['pwc']:
            print w

    def infer_one(self, user_id):
        tweets = self.tweets.get(user_id)
        user_words = {}
        for tweet in tweets:
            for w in Util.get_nouns(tweet['text'], params['lang']):
                if not w in user_words: user_words[w] = 0
                user_words[w] += 1
        city_probs = {}
        for w in self.model['pwc']:
            for city in self.model['pwc'][w]:
                if not city in city_probs:
                    city_probs[city] = self.model['pc'][city]
                city_probs[city] *= self.model['pwc'][w][city]

        max_city = None
        max_prob = 0
        for city in city_probs:
            if max_prob < city_probs[city]:
                max_prob = city_probs[city]
                max_city = city
        return Util.str_to_tuple(max_city)

    def infer(self, params):
        for user in self.users.iter():
            if user['location_point'] == None:
                user['location_point'] = self.infer_one(user['id'])

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

    method = Hecht(users, tweets)
    model = method.calgari({'minu':30, 'max_count':10000, 'lang':'en'})
    method.set_model(model)
    method.model_dump()
    f = open('calgari.us.model', 'w')
    pickle.dump(model, f)
    f.close()
