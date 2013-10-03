import math
from lib.util import Util

class LMM:
    def __init__(self, users, graph):
        self.users = users
        self.graph = graph
        self.in_dominance_distributions = {}
        self.out_dominance_distributions = {}

    def norm_pdf(self, x, median, var):
        p = (1/(2*math.pi*(var+1))) * math.exp(( (x[0] - median[0])**2 + (x[1] - median[1])**2 ) / (-2 * (var+1)))
        return p

    def find_mode(self, lmm):
        max_prob = -1
        mode = None
        for component in lmm:
            candidate = component['median']
            p = sum([self.norm_pdf(candidate, c['median'], c['var']) for c in lmm])
            if p > max_prob:
                max_prob = p
                mode = candidate
        return (mode, max_prob)

    def calc_centroid(self, points):
        lat_sum = sum([p[0] for p in points])
        lng_sum = sum([p[1] for p in points])
        return (lat_sum/len(points), lng_sum/len(points))

    def calc_medoid(self, points):
        centroid = self.calc_centroid(points)
        min_d = 1000000000000000
        min_p = None
        for p in points:
            d = (p[0] - centroid[0])**2 + (p[1] - centroid[1])**2
            if d < min_d:
                min_p = p
        return min_p
    
    def calc_variance(self, median, points):
        s = sum([(p[0] - median[0])**2 + (p[1] - median[1])**2 for p in points])
        return s / (2*len(points))

    def calc_dominance_distributions(self, direction, params):
        for user in self.users.iter():
            if direction == 'in':
                neighbors = self.graph.get_followers(user['id'])
            elif direction == 'out':
                neighbors = self.graph.get_friends(user['id'])

            points = []
            for neighbor_id in neighbors:
                neighbor = self.users.get(neighbor_id)
                if neighbor['location_point'] != None:
                    points.append(neighbor['location_point'])

            centrality = len(neighbors)

            if centrality > params['c0'] and len(points) > 0:
                median = self.calc_medoid(points)
                var = self.calc_variance(median, points)
                if direction == 'in':
                    self.in_dominance_distributions[user['id']] = {'var':var, 'median':median}
                elif direction == 'out':
                    self.out_dominance_distributions[user['id']] = {'var':var, 'median':median}

    def infer_one(self, user_id, params):
        lmm = []
        for fid in self.graph.get_followers(user_id):
            if fid in self.out_dominance_distributions:
                lmm.append(self.out_dominance_distributions[fid])
        for fid in self.graph.get_friends(user_id):
            if fid in self.in_dominance_distributions:
                lmm.append(self.in_dominance_distributions[fid])
        mode, mode_prob = self.find_mode(lmm)
        if mode_prob > params['p0']:
            return mode
        else:
            return None

    def infer(self, params):
        self.calc_dominance_distributions('in', params)
        self.calc_dominance_distributions('out', params)
        for user in self.users.iter():
            if user['location_point'] == None:
                user['location_point'] = self.infer_one(user['id'], params)

    def get_users(self):
        return self.users


if __name__ == '__main__':
    import sys
    from lib.users import Users
    from lib.graph import Graph

    if len(sys.argv) < 3:
        print '[usage]: python %s [users file path] [graph file path]' % sys.argv[0]
        exit()

    users = Users()
    users.load_file(sys.argv[1])
    graph = Graph()
    graph.load_file(sys.argv[2])

    lmm = LMM(users, graph)
    lmm.infer()
    print lmm.get_users()
