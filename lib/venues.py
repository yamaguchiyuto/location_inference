import json

class Venues:
    def __init__(self, db):
        self.db = db
        self.values = self.load_mysql(db)

    def load_mysql(self, db):
        query = "SELECT name FROM venues"
        result = db.issue_select(query)
        venues = []
        for row in result:
            venues.append(row['name'].lower())
        return venues

    def get_point(self, name):
        query = "SELECT * FROM venues WHERE name = '%s'" % name
        result = self.db.issue_select(query)
        if type(result) == type(()) and len(result) > 0:
            return (result[0]['latitude'], result[0]['longitude'])
        else:
            return None

    def iter(self):
        for venue in self.values:
            yield venue

    def get_users(self, venue_name):
        query = "SELECT user_id FROM venue_graph WHERE venue = '%s'" % venue_name
        result = self.db.issue_select(query)
        users = []
        for row in result:
            users.append(row['user_id'])
        return users

    
    def get_venues(self, user_id):
        query = "SELECT venue FROM venue_graph WHERE user_id = %s" % user_id
        result = self.db.issue_select(query)
        venues = []
        for row in result:
            venues.append(row['venue'].lower())
        return venues 

if __name__ == '__main__':
    import sys

    db = DB(sys.argv[1], sys.argv[2], sys.argv[3])
    venues = Venues(db)
