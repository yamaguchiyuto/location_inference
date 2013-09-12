from lib.util import Util

class Jurgens:
    def __init__(self, users, graph):
        self.users = users
        self.graph = graph
        self.mapping = self.init_mapping()

    def init_mapping(self):
        mapping = {}
        for user in self.users.iter():
            mapping[user['id']] = user['location_point']
        return mapping


    def select(self, user):
        friends = set(self.graph.get_friends(user['id']))
        followers = set(self.graph.get_followers(user['id']))
        neighbors = friends | followers
        locations = []
        for neighbor_id in neighbors:
            if self.mapping[neighbor_id] != None:
                locations.append(self.mapping[neighbor_id])
        if len(locations) > 0:
            geometric_median = Util.calc_medoid(locations)
            return geometric_median
        else:
            return None

    def infer(self, params):
        i = 1
        while True:
            for user in self.users.iter():
                if user['location_point'] == None:
                    self.mapping[user['id']] = self.select(user)
            if i >= params['niter']:
                break
            i += 1
        for user in self.users.iter():
            user['location_point'] = self.mapping[user['id']]

    def get_users(self):
        return self.users


if __name__ == '__main__':
    import sys
    from lib.users import Users
    from lib.graph import Graph

    if len(sys.argv) < 3:
        print '[usage]: python %s [user filepath] [graph filepath]' % sys.argv[0]
        exit()

    users = Users()
    users.load_file(sys.argv[1])
    graph = Graph()
    graph.load_file(sys.argv[2])
    jg = Jurgens(users, graph)
    jg.infer({'niter':4})
