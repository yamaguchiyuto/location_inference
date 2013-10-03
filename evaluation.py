from lib.util import Util

class Evaluation:
    def __init__(self, test_users):
        self.test_users = test_users

    def calc_error_distances(self, inferred_users):
        error_distances = []
        for test_user in self.test_users.iter():
            true_point = test_user['location_point']
            inferred_user = inferred_users.get(test_user['id'])
            if inferred_user != None:
                inferred_point = inferred_user['location_point']
                if inferred_point != None:
                    error_distance = Util.hubeny_distance(inferred_point, true_point)
                    error_distances.append(error_distance)
        return error_distances

    def mean_error_distance(self, error_distances):
        error_sum = sum([e for e in error_distances])
        return error_sum / float(len(error_distances))
    
    def median_error_distance(self, error_distances):
        error_distances.sort()
        return error_distances[len(error_distances)/2]

    def precision_and_recall(self, error_distances, distance_threshold):
        correct = sum([1 for e in error_distances if e < distance_threshold])
        precision = float(correct) / len(error_distances)
        recall = float(len(error_distances)) / len(test_users)
        return (precision, recall)

if __name__ == '__main__':
    import sys
    import pickle
    import json
    from lib.users import Users
    from lib.graph import Graph
    from lib.words import Words
    from lib.tweets_db import Tweets
    from lib.venues import Venues
    from lib.db import DB

    from li_kdd12.udi import UDI
    from jurgens_icwsm13.jurgens import Jurgens
    from cheng_cikm10.cheng import Cheng
    from naiveg.naiveg import NaiveG
    from naivec.naivec import NaiveC
    from olim.olim import OLIM 
    from olimg.olimg import OLIMG
    from yamaguchi_cosn13.lmm import LMM
    from hecht_chi11.hecht import Hecht

    def load_params(filepath):
        f = open(filepath, 'r')
        params = json.loads(f.read().rstrip())
        f.close()
        return params

    if len(sys.argv) < 2:
        print '[usage]: python %s param:value ...' % sys.argv[0]
        print 'test: test user filepath'
        print 'training: training user filepath'
        print 'graph: graph filepath'
        print 'lwords: lwords filepath'
        print 'model: model filepath'
        print 'params: params filepath'
        print 'dbuser: db user name'
        print 'dbpass: db pass'
        print 'dbname: db name'
        print 'method: method name'
        print '\tnaiveg'
        print '\tnaivec'
        print '\tli'
        print '\tjurgens'
        print '\tcheng'
        print '\tbackstrom'
        print '\tolim'
        print '\tolimg'
        print '\tlmm'
        print '\thecht'
        exit()

    args = {}
    for i in range(1, len(sys.argv)):
        key, value = sys.argv[i].split(':')
        args[key] = value

    test_users = Users()
    test_users.load_file(args['test'])
    training_users = Users()
    training_users.load_file(args['training'])
    ev = Evaluation(test_users)

    if args['method'] == 'naiveg':
        graph = Graph()
        graph.load_file(args['graph'])
        method = NaiveG(training_users, graph)
    elif args['method'] == 'naivec':
        db = DB(args['dbuser'], args['dbpass'], args['dbname'])
        tweets = Tweets(db)
        venues = Venues(db)
        method = NaiveC(training_users, tweets, venues)
    elif args['method'] == 'li':
        db = DB(args['dbuser'], args['dbpass'], args['dbname'])
        tweets = Tweets(db)
        venues = Venues(db)
        graph = Graph()
        graph.load_file(args['graph'])
        method = UDI(training_users, tweets, venues, graph)
    elif args['method'] == 'jurgens':
        graph = Graph()
        graph.load_file(args['graph'])
        method = Jurgens(training_users, graph)
    elif args['method'] == 'cheng':
        db = DB(args['dbuser'], args['dbpass'], args['dbname'])
        lwords = Words()
        lwords.load_file(args['lwords'])
        tweets = Tweets(db)
        method = Cheng(training_users, tweets, lwords)
    elif args['method'] == 'backstrom':
        graph = Graph()
        graph.load_file(args['graph'])
        method = Backstrom(training_users, graph)
    elif args['method'] == 'olim':
        db = DB(args['dbuser'], args['dbpass'], args['dbname'])
        lwords = Words()
        lwords.load_file(args['lwords'])
        tweets = Tweets(db)
        f = open(args['model'], 'r')
        model = pickle.load(f)
        f.close()
        method = OLIM(training_users, tweets, model, lwords)
    elif args['method'] == 'olimg':
        db = DB(args['dbuser'], args['dbpass'], args['dbname'])
        lwords = Words()
        lwords.load_file(args['lwords'])
        tweets = Tweets(db)
        graph = Graph()
        graph.load_file(args['graph'])
        f = open(args['model'], 'r')
        model = pickle.load(f)
        f.close()
        method = OLIMG(training_users, tweets, graph, model, lwords)
    elif args['method'] == 'lmm':
        graph = Graph()
        graph.load_file(args['graph'])
        method = LMM(training_users, graph)
    elif args['method'] == 'hecht':
        db = DB(args['dbuser'], args['dbpass'], args['dbname'])
        tweets = Tweets(db)
        f = open(args['model'], 'r')
        model = pickle.load(f)
        f.close()
        method = Hecht(training_users, tweets, model)
    else:
        print 'invalid method name'
        exit()

    params = load_params(args['params'])

    method.infer(params)
    inferred_users = method.get_users()
    if len(inferred_users) == 0:
        print 'no reuslt'
    else:
        error_distances = ev.calc_error_distances(inferred_users)
        mean_ed = ev.mean_error_distance(error_distances)
        median_ed = ev.median_error_distance(error_distances)
        p, r = ev.precision_and_recall(error_distances, 160000) 
        f = (2*p*r) / (p+r)
        print json.dumps(args)
        print json.dumps(params)
        print "Mean ED: %f" % mean_ed
        print "Median ED: %f" % median_ed
        print "Precision: %f" % p
        print "Recall: %f" % r
        print "F-measure: %f" % f
        for e in error_distances:
            print e
