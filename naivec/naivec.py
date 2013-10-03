from lib.util import Util

class NaiveC:
    def __init__(self, users, tweets, venues):
        self.users = users
        self.tweets = tweets
        self.venues = venues

    def infer_one(self, user_id):
        points = []
        user_venues = self.venues.get_venues(user_id)
        for venue_name in user_venues:
            p = self.venues.get_point(venue_name)
            points.append(p)
        if len(points) > 0:
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
    from lib.db import DB
    from lib.users import Users
    from lib.tweets_db import Tweets
    from lib.venues import Venues

    if len(sys.argv) < 3:
        print '[usage]: python %s [users file path] [db user name] [db pass] [db name]' % sys.argv[0]
        exit()
    
    users = Users()
    users.load_file(sys.argv[1])
    db = DB(sys.argv[2], sys.argv[3], sys.argv[4])
    tweets = Tweets(db)
    venues = Venues(db)

    method = NaiveC(users, tweets, venues)
    method.infer()
