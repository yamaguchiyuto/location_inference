import random
from lib.util import Util

class UDI:
    def __init__(self, users, tweets, venues, graph):
        self.users = users
        self.tweets = tweets
        self.venues = venues
        self.graph = graph
        self.user_locations = {}
        self.user_variances = {}
        self.venue_variances = {}

    def init_user_location(self):
        lat = random.uniform(25.0, 45.0)
        lng = random.uniform(125.0, 145.0)
        return [lat, lng]

    def user_variance(self, user):
        points = []
        v = 1.0
        if user['location_point'] == None:
            p = self.user_locations[user['id']]
        else:
            p = user['location_point']
        for follower_id in self.graph.get_followers(user['id']):
            follower = self.users.get(follower_id)
            if follower != None:
                location = follower['location_point']
                if location != None:
                    points.append(location)
        if len(points) > 1:
            for q in points:
                v += (p[0] - q[0])**2 + (p[1] - q[1])**2
            return v / (2*len(points))
        else:
            return 1.0

    def calc_user_variances(self):
        user_variances = {}
        for user in self.users.iter():
            user_variances[user['id']] = self.user_variance(user)
        return user_variances

    def venue_variance(self, venue_name):
        points = []
        v = 1.0
        p = self.venues.get_point(venue_name)
        for user_id in self.venues.get_users(venue_name):
            user = self.users.get(user_id)
            if user != None:
                location = user['location_point']
                if location != None:
                    points.append(location)
        if len(points) > 1:
            for q in points:
                v += (p[0] - q[0])**2 + (p[1] - q[1])**2
            return v / (2*len(points))
        else:
            return 1.0

    def calc_venue_variances(self):
        venue_variances = {}
        for venue_name in self.venues.iter():
            venue_variances[venue_name] = self.venue_variance(venue_name)
        return venue_variances

    def calc_user_location(self, user, params):
        numx = 0
        numy = 0
        den = 0
        if params['signal'] in ['a', 'g']:
            for follower_id in self.graph.get_followers(user['id']):
                follower = self.users.get(follower_id)
                if follower != None:
                    p = follower['location_point']
                    if p == None: p = self.user_locations[follower['id']]
                    v = self.user_variances[follower['id']]
                    numx  += p[0] / v
                    numy  += p[1] / v
                    den += 1.0 / v
            for friend_id in self.graph.get_friends(user['id']):
                friend = self.users.get(friend_id)
                if friend != None:
                    p = friend['location_point']
                    if p == None: p = self.user_locations[friend['id']]
                    v = self.user_variances[friend['id']]
                    numx += p[0] / v
                    numy += p[1] / v
                    den += 1.0 / v
        if params['signal'] in ['a', 'c']:
            for venue_name in self.venues.get_venues(user['id']):
                p = self.venues.get_point(venue_name)
                v = self.venue_variances[venue_name.lower()]
                numx += p[0] / v
                numy += p[1] / v
                den += 1.0 / v
        if den > 0:
            return (numx/den, numy/den)
        else:
            return self.user_locations[user['id']]


    def calc_user_locations(self, params):
        user_locations = {}
        for user in self.users.iter():
            if user['location_point'] == None:
                user_locations[user['id']] = self.calc_user_location(user, params)
        return user_locations

    def calc_err(self, l, r):
        err = 0.0
        for k in l:
            p = l[k]
            q = r[k]
            err += (p[0] - q[0])**2 + (p[1] - q[1])**2
        return err / len(l)

    def infer(self, params):
        for user in self.users.iter():
            if user['location_point'] == None:
                self.user_locations[user['id']] = self.init_user_location()
        while True:
            self.user_variances = self.calc_user_variances()
            self.venue_variances = self.calc_venue_variances()
            n_iter = 0
            while True:
                next_user_locations = self.calc_user_locations(params)
                inner_err = self.calc_err(self.user_locations, next_user_locations)
                self.user_locations = next_user_locations
                n_iter += 1
                if inner_err < params['inner_th']:
                    break
            if n_iter == 1:
                break
        for user in self.users.iter():
            if user['location_point'] == None:
                user['location_point'] = self.predict(user['id'])

    def predict(self, user_id):
        min_d = 100000000
        min_p = None
        p = self.user_locations[user_id]
        for follower_id in self.graph.get_followers(user_id):
            follower = self.users.get(follower_id)
            if follower != None:
                follower_p = follower['location_point']
                if follower_p != None:
                    d = Util.hubeny_distance(follower_p, p)
                    if min_d > d:
                        min_d = d
                        min_p = follower_p
        for friend_id in self.graph.get_friends(user_id):
            friend = self.users.get(friend_id)
            if friend != None:
                friend_p = friend['location_point']
                if friend_p != None:
                    d = Util.hubeny_distance(friend_p, p)
                    if min_d > d:
                        min_d = d
                        min_p = friend_p 
        for venue_name in self.venues.get_venues(user_id):
            venue_p = self.venues.get_point(venue_name)
            d = Util.hubeny_distance(venue_p, p)
            if min_d > d:
                min_d = d
                min_p = venue_p 


        return min_p

    def get_users(self):
        return self.users

if __name__ == '__main__':
    import sys
    from lib.db import DB
    from lib.users import Users
    from lib.tweets_db import Tweets
    from lib.venues import Venues
    from lib.graph import Graph

    if len(sys.argv) < 3:
        print '[usage]: python %s [users filepath] [graph filepath]  [db user name] [db pass] [db name]' % sys.argv[0]
        exit()
    
    users = Users()
    users.load_file(sys.argv[1])
    graph = Graph()
    graph.load_file(sys.argv[2])
    db = DB(sys.argv[3], sys.argv[4], sys.argv[5])
    tweets = Tweets(db)
    venues = Venues(db)

    method = UDI(users, tweets, venues, graph)
    method.infer({'inner_th':0.001, 'signal':'a'})
