from lib.util import Util

class NaiveC:
    def __init__(self, users, tweets, venues):
        self.users = users
        self.tweets = tweets
        self.venues = venues

    def extract_venues(self, user_tweets):
        words = set([])
        venue_points = []
        for tweet in user_tweets:
            for w in Util.get_place_names(tweet['text'].decode('utf8')):
                words.add(w)
        for w in words:
            venue_point = self.venues.get_point(w)
            if venue_point != None:
                venue_points.append(venue_point)
        return venue_points

    def infer_one(self, user_id):
        user_tweets = self.tweets.get(user_id)
        points = self.extract_venues(user_tweets) 
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
