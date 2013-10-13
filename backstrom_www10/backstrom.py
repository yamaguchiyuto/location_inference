import math
from lib.util import Util

class Backstrom:
    def __init__(self, users, graph, model):
        self.users = users
        self.graph = graph
        self.model = model

    def edge_prob(self, d, a=0.0019, b=0.196, c=-1.05):
        return a * (d + b) ** c

    def compute_gamma(self):
        """ returns log gammma values """
        gamma = {}
        locations = set([])
        for user in self.users.iter():
            if user['location_point'] != None:
                locations.add(tuple(user['location_point']))
        for l in locations:
            gamma[l] = 0
            for user in self.users.iter():
                d = Util.hubeny_distance(l, user['location_point'])
                gamma[l] += math.log(1 - self.edge_prob(d))
        return gamma

    def compute_gamma_u(self, user):
        gamma_u = {}
        friends = self.graph.get_friends(user['id'])
        followers = self.graph.get_followers(user['id'])
        neighbors = set(friends) | set(followers)
        for vid in neighbors:
            v = self.users.get(vid)
            if v != None and v['location_point'] != None:
                if not tuple(v['location_point']) in gamma_u:
                    gamma_u[tuple(v['location_point'])] = 0
                    for wid in neighbors:
                        w = self.users.get(wid)
                        if w != None and w['location_point'] != None:
                            d = Util.hubeny_distance(w['location_point'], v['location_point'])
                            p = self.edge_prob(d)
                            gamma_u[tuple(v['location_point'])] += math.log(p) - math.log(1-p)
        return gamma_u

    def infer_one(self, user):
        gamma_u = self.compute_gamma_u(user)
        max_location = None
        max_likelihood = -100000000000
        for l, v in gamma_u.items():
            likelihood = v + self.model[l]
            if max_likelihood < likelihood:
                max_likelihood = likelihood
                max_location = l
        return max_location

    def infer(self, params):
        for user in self.users.iter():
            if user['location_point'] == None:
                user['location_point'] = self.infer_one(user)

    def get_users(self):
        return self.users


if __name__ == '__main__':
    import sys
    import pickle
    from lib.users import Users
    from lib.graph import Graph

    if len(sys.argv) < 3:
        print '[usage]: python %s [users file path] [graph file path]' % sys.argv[0]
        exit()

    users = Users()
    users.load_file(sys.argv[1])
    graph = Graph()
    graph.load_file(sys.argv[2])

    method = Backstrom(users, graph)
    model = method.compute_gamma()
    f = open('backstrom.model', 'w')
    pickle.dump(model, f)
    f.close()

