import numpy
from lib.util import Util
from lib.words import Words

class OLIMG:
    def __init__(self, users, tweets, graph, model, lwords):
        self.users = users
        self.user_distributions = {}
        self.tweets = tweets
        self.graph = graph
        self.model = model # GMM in scikit-learn
        self.lwords = lwords # local words if extracted previously
        self.regular_sum = self.calc_regular_sum()

    def calc_regular_sum(self):
        return sum([v**2 for v in self.model.weights_])

    def extract_local_words_batch(self, params):
        lwords = {}
        word_counts = {}

        for user in self.users.iter():
            location = user['location_point']
            if location != None:
                city = str(self.model.predict([location])[0])
                tweets = self.tweets.get(user['id'])
                user_words = set([])
                for tweet in tweets:
                    user_words |= set(Util.get_words(tweet['text']))
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
                d = self.calc_divergence(N, word_counts[w], params)
                if self.check_divergence(d, params) == True:
                        lwords[w] = {'word':w, 'd':d, 'distribution':word_counts[w]} # save as dict
        return Words(lwords)



    def extract_local_words_(self, tweets, params):
        lwords = {}
        word_counts = {}

        word_sets = {}
        for tweet in tweets:
            if not tweet['user_id'] in word_sets: word_sets[tweet['user_id']] = set([])
            words = Util.get_words(tweet['text'])
            word_sets[tweet['user_id']] |= set(words)

        for user_id in word_sets:
            user = self.users.get(user_id)
            if user != None:
                location = user['location_point']
                if location != None:
                    city = str(self.model.predict([location])[0])
                    for w in word_sets[user_id]:
                        if not w in word_counts: word_counts[w] = {}
                        if not city in word_counts[w]: word_counts[w][city] = 0
                        word_counts[w][city] += 1

        """ calculating divergences """
        for w in word_counts:
            N = float(sum([v for v in word_counts[w].values()]))
            if N >= params['cmin']:
                d = self.calc_divergence(N, word_counts[w], params)
                if self.check_divergence(d, params) == True:
                        lwords[w] = {'word':w, 'd':d, 'distribution':word_counts[w]} # save as dict
        return Words(lwords)



    def extract_local_words(self, tweets, params):
        lwords = {}
        word_counts = {}

        """ making user sets """
        user_sets = {}
        for tweet in tweets:
            words = Util.get_words(tweet['text'])
            for w in words:
                if not w in user_sets: user_sets[w] = set([])
                user_sets[w].add(tweet['user_id'])

        """ making word distributions """
        for w in user_sets:
            for user_id in user_sets[w]:
                user = self.users.get(user_id)
                if user != None:
                    location = user['location_point']
                    if location != None:
                        """ labeled user """
                        if not w in word_counts: word_counts[w] = {}
                        city = str(self.model.predict([location])[0])
                        if not city in word_counts[w]: word_counts[w][city] = 0
                        word_counts[w][city] += 1

        """ calculating divergences """
        for w in word_counts:
            N = float(sum([v for v in word_counts[w].values()]))
            if N >= params['cmin']:
                d = self.calc_divergence(N, word_counts[w], params)
                if self.check_divergence(d, params) == True:
                        lwords[w] = {'word':w, 'd':d, 'distribution':word_counts[w]} # save as dict
        return Words(lwords)

    def calc_divergence(self, n, word_count, params):
        if params['divergence'] == 'l2':
            d = Util.l2dist_fast(self.regular_sum, self.model.weights_, n, word_count)
            return d
        elif params['divergence'] == 'kl':
            d = Util.kl_div_fast(self.model.weights_, n, word_count)
            return d
        elif params['divergence'] == 'dispersion':
            points = [self.model.means_[int(k)] for k,v in word_count.items() for i in range(0, v)]
            d = Util.calc_dispersion(points)
            return d
        else:
            print 'invalid divergence'
            exit()

    def check_divergence(self, d, params):
        if params['divergence'] == 'l2':
            if d >= params['dmin']:
                return True
            else:
                return False
        elif params['divergence'] == 'kl':
            if d >= params['dmin']:
                return True
            else:
                return False
        elif params['divergence'] == 'dispersion':
            if d <= params['dmin']:
                return True
            else:
                return False
        else:
            print 'invalid divergence'
            exit()


    def get_neighbors(self, user_id, params):
        if params['neighbors'] == 'followers':
            return set(self.graph.get_followers(user_id))
        elif params['neighbors'] == 'friends':
            return set(self.graph.get_friends(user_id))
        elif params['neighbors'] == 'all':
            return set(self.graph.get_followers(user_id)) | set(self.graph.get_friends(user_id))
        elif params['neighbors'] == 'mutual':
            return set(self.graph.get_followers(user_id)) & set(self.graph.get_friends(user_id))
        elif params['neighbors'] == 'none':
            return set([])
        else:
            print 'invalid neighbors parameter'
            exit()


    def update_user_distributions(self, tweets, tlwords, params):
        for tweet in tweets:
            neighbors = self.get_neighbors(tweet['user_id'], params)
            users = neighbors | set([tweet['user_id']])
            for user_id in users:
                user = self.users.get(user_id)
                if user != None:
                    if user['location_point'] == None:
                        """ unlabeled users """
                        if not user['id'] in self.user_distributions:
                            self.user_distributions[user['id']] = self.init_user_distribution()
                        words = Util.get_words(tweet['text'])
                        for w in words:
                            if tlwords.contain(w):
                                """ update using temporally-local word """
                                tlword = tlwords.get(w)
                                self.user_distributions[user['id']] = self.add_distribution(self.user_distributions[user['id']], tlword['distribution'])
                            if self.lwords.contain(w):
                                """ update using local word """
                                lword = self.lwords.get(w)
                                if params['divergence'] in ['l2', 'kl']:
                                    if lword['d'] >= params['dmin']:
                                        self.user_distributions[user['id']] = self.add_distribution(self.user_distributions[user['id']], lword['distribution'])
                                else:
                                    if lword['d'] <= params['dmin']:
                                        self.user_distributions[user['id']] = self.add_distribution(self.user_distributions[user['id']], lword['distribution'])


    def add_distribution(self, p, q):
        for k in q:
            if not k in p: p[k] = 0
            p[k] += q[k]
        return p

    def init_user_distribution(self):
        return {}

    def predict(self, user_distribution, params):
        B = numpy.array(self.model.weights_) * params['r']
        for k in user_distribution:
            B[int(k)] += user_distribution[k]
        if params['predict'] == 'max':
            pass
        elif params['predict'] == 'div':
            B = B / B.sum() # normalize
            regular = numpy.array(self.model.weights_)
            B = B / regular
        elif params['predict'] == 'sub':
            B = B / B.sum() # normalize
            regular = numpy.array(self.model.weights_)
            B = B - regular
        else:
            print 'invalid prediction method'
            exit()
        return B.argmax()

    def infer(self, params):
        window = {'tweets':[], 'start':0} # storing tweets

        """ User distribution updating """
        for tweet in self.tweets.stream():
            if type(tweet) == type({}) and 'timestamp' in tweet:
                current_time = Util.str_to_unixtime(Util.time_to_str(tweet['timestamp']))
                window['tweets'].append(tweet)
                if current_time - window['start'] > params['window_size']:
                    if params['tl']:
                        """ use tl-words """
                        tlwords = self.extract_local_words_(window['tweets'], params)
                    else:
                        """ dont use tl-words """
                        tlwords = Words()
                    self.update_user_distributions(window['tweets'], tlwords, params)
                    window = {'tweets':[], 'start':current_time}

        """ Location prediction using user distribution """
        for user in self.users.iter():
            if user['location_point'] == None:
                """ unlabeled user """
                if user['id'] in self.user_distributions and len(self.user_distributions[user['id']]) > 0:
                    inferred_city = self.predict(self.user_distributions[user['id']], params)
                    inferred_location = self.model.means_[inferred_city]
                    user['location_point'] = inferred_location
                else:
                    if params['default']:
                        """ no clues            """
                        """ predict using prior """
                        inferred_city = self.predict({}, params)
                        inferred_location = self.model.means_[inferred_city]
                        user['location_point'] = inferred_location

    def get_users(self):
        return self.users

if __name__ == '__main__':
    import sys
    import pickle
    from lib.db import DB
    from lib.users import Users
    from lib.tweets_db import Tweets
    from lib.words import Words

    if len(sys.argv) < 6:
        print '[usage]: python %s [users file path] [db user name] [db pass] [db name] [model filepath]' % sys.argv[0]
        exit()

    users = Users()
    users.load_file(sys.argv[1])
    db = DB(sys.argv[2], sys.argv[3], sys.argv[4])
    tweets = Tweets(db)
    lwords = Words()

    f = open(sys.argv[5], 'r')
    model = pickle.load(f)
    f.close()

    tl = OLIM(users, tweets, model, lwords)
    #print tl.extract_local_words({'dmin':0.05, 'cmin':30})
    #print tl.extract_local_words_(tl.tweets.stream(), {'dmin':0.05, 'cmin':30, 'window_size':1800, 'tl':False, 'default':False, 'divergence':'l2'})
    #print tl.extract_local_words_batch({'dmin':300000, 'cmin':30, 'window_size':1800, 'tl':False, 'default':False, 'divergence':'dispersion'})
    print tl.extract_local_words_batch({'dmin':0.1, 'cmin':30, 'window_size':10800, 'tl':False, 'default':False, 'divergence':'kl'})
    #print tl.extract_local_words_batch({'dmin':1.0, 'cmin':30, 'window_size':1800, 'tl':False, 'default':False, 'divergence':'kl'})
    #print tl.extract_local_words_batch({'dmin':300000, 'cmin':30, 'window_size':1800, 'tl':False, 'default':False, 'divergence':'dispersion'})

