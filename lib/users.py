import json

class Users:
    def __init__(self):
        self.values = {}

    def load_file(self, filepath):
        for line in open(filepath, 'r'):
            user = json.loads(line.rstrip())
            self.values[user['id']] = user
    
    def load_mysql(self, mysqldb):
        pass

    def load_mongodb(self, mongodb):
        pass
    
    def get(self, user_id):
        return self.values[user_id]

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print '[usage]: python %s [user file path]' % sys.argv[0]
        exit()


    users = Users()
    users.load_file(sys.argv[1])
    print users.get(2)
