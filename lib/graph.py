import json

class Graph:
    def __init__(self):
        self.forward = {}
        self.backward = {}

    def load_file(self, filepath):
        for line in open(filepath, 'r'):
            edges = json.loads(line.rstrip())
            self.forward[edges["src_id"]] = edges["dst_ids"]
            for dst_id in edges["dst_ids"]:
                if not dst_id in self.backward: self.backward[dst_id] = []
                self.backward[dst_id].append(edges["src_id"])
    
    def load_mysql(self, mysqldb):
        pass

    def load_mongodb(self, mongodb):
        pass
    
    def get_followers(self, user_id):
        if user_id in self.backward:
            return tuple(self.backward[user_id])
        else:
            return ()

    def get_friends(self, user_id):
        if user_id in self.forward:
            return tuple(self.forward[user_id])
        else:
            return ()

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print '[usage]: python %s [graph file path]' % sys.argv[0]
        exit()

    graph = Graph()
    graph.load_file(sys.argv[1])
    print graph.get_friends(2)
    print graph.get_followers(0)
    print graph.get_followers(1)
    print graph.get_followers(2)
    print graph.get_followers(3)
    print graph.get_followers(4)
