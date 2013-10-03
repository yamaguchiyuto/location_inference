import json

class Graph:
    def __init__(self):
        self.forward = {}
        self.backward = {}

    def __str__(self):
        res = ""
        for src_id in self.forward:
            res += json.dumps({'src_id':src_id, 'dst_ids':self.forward[src_id]}) + "\n"
        return res[:-1]

    def load_file(self, filepath):
        for line in open(filepath, 'r'):
            edges = json.loads(line.rstrip())
            self.forward[edges["src_id"]] = edges["dst_ids"]
            for dst_id in edges["dst_ids"]:
                if not dst_id in self.backward: self.backward[dst_id] = []
                self.backward[dst_id].append(edges["src_id"])
    
    def load_mysql(self, mysqldb, users):
        for user in users.iter():
            query = "SELECT * FROM graph WHERE src_id = %s" % user['id']
            result = mysqldb.issue_select(query)
            if type(result) == type(()):
                self.forward[user['id']] = [v['dst_id'] for v in result if users.contain(v['dst_id'])]
                for dst_id in self.forward[user['id']]:
                    if not users.contain(dst_id): continue
                    if not dst_id in self.backward: self.backward[dst_id] = []
                    self.backward[dst_id].append(user['id'])

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

    def followers_iter(self):
        for dst_id in self.backward:
            for src_id in self.backward[dst_id]:
                yield (dst_id, src_id)

    def friends_iter(self):
        for src_id in self.forward:
            for dst_id in self.forward[src_id]:
                yield (src_id, dst_id)

if __name__ == '__main__':
    import sys
    from users import Users
    from db import DB

    if len(sys.argv) < 5:
        print '[usage]: python %s [users filepath] [dbuser] [dbpass] [dbname]' % sys.argv[0]
        exit()

    users = Users()
    users.load_file(sys.argv[1])
    graph = Graph()
    graph.load_mysql(DB(sys.argv[2], sys.argv[3], sys.argv[4]), users)
    c = 0
    for e in graph.followers_iter():
        c += 1
    print c

