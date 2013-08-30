import lib.util as util

class NaiveG:
    def __init__(self, users, graph):
        self.users = users
        self.graph = graph

    def infer(self, user_id):
        points = []
        for fid in self.graph.get_followers(user_id):
            user = self.users.get(fid)
            points.append(user['location_point'])
        if len(points) > 0:
            centroid = util.calc_centroid(points)
            return centroid
        else:
            return None

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
    print ng.infer(0)
    print ng.infer(1)
    print ng.infer(2)
    print ng.infer(3)
    print ng.infer(4)
