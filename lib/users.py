import json

class Users:
    def __init__(self):
        self.values = {}

    def __str__(self):
        res = ""
        for user in self.values.values():
            res += json.dumps(user) + "\n"
        return res[:-1]

    def __len__(self):
        return len(self.values)

    def load_file(self, filepath):
        for line in open(filepath, 'r'):
            user = json.loads(line.rstrip())
            self.values[user['id']] = user

    def load_mysql(self, mysqldb):
        query = "SELECT id, latitude, longitude FROM users"
        result = mysqldb.issue_select(query)
        for user in result:
            if user['latitude'] != None:
                    self.values[user['id']] = {'id':user['id'], 'location_point':[user['latitude'], user['longitude']]}
   
    def load_mongodb(self, mongodb):
        pass
    
    def get(self, user_id):
        if user_id in self.values:
            return self.values[user_id]
        else:
            return None
    
    def contain(self, user_id):
        if user_id in self.values:
            return True
        else:
            return False

    def iter(self):
        for user in self.values.values():
            yield user

if __name__ == '__main__':
    import sys
    from db import DB

    if len(sys.argv) < 4:
        print '[usage]: python %s [db user name] [db pass] [db name]' % sys.argv[0]
        exit()


    db = DB(sys.argv[1], sys.argv[2], sys.argv[3])
    users = Users()
    users.load_mysql(db)
    print users
