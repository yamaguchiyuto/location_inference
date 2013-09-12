from lib.util import Util

class NaiveG:
    def __init__(self, users, graph):
        self.users = users
        self.graph = graph

    def infer_one(self, user_id):
        points = []
        for fid in self.graph.get_followers(user_id):
            user = self.users.get(fid)
            if user != None:
                if user['location_point'] != None:
                    points.append(user['location_point'])
        if len(points) > 0:
            #centroid = Util.calc_centroid(points)
            centroid = Util.calc_medoid(points)
            return centroid
        else:
            return None

    def infer(self, params):
        for user in self.users.iter():
            if user['location_point'] == None:
                user['location_point'] = self.infer_one(user['id'])

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

    ng = NaiveG(users, graph)
    ng.infer()
    print ng.get_users()
