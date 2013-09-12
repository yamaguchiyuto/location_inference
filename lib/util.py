# -*- coding: utf-8 -*-
import math
import re
import time
import MeCab
from osmapi import OsmApi

class Util:
    tagger = MeCab.Tagger('-Ochasen')
    osmapi = OsmApi()

    @classmethod
    def get_venue_point(self, w):
        result = self.osmapi.get(w)
        if len(result) > 0:
            return (float(result[0]['lat']), float(result[0]['lon']))
        else:
            None

    @classmethod
    def remove_usernames_and_urls(self, text):
        username_removed_text = re.sub('@\w+', '', text) # remove usernames
        return re.sub('(https?|ftp)(:\/\/[-_.!~*\'()a-zA-Z0-9;\/?:\@&=+\$,%#]+)', '', username_removed_text) # remove urls

    @classmethod
    def get_words(self, text):
        words = []
        node = self.tagger.parseToNode(self.remove_usernames_and_urls(text))
        while node:
            if node.feature.split(',')[0] == '名詞':
                words.append(node.surface)
            node = node.next
        return words

    @classmethod
    def get_place_names(self, text):
        words = []
        node = self.tagger.parseToNode(text.encode('utf8'))
        while node:
            if node.feature.split(',')[1] == '固有名詞' and node.feature.split(',')[2] == '地域':
                words.append(node.surface)
            node = node.next
        return words

    @classmethod
    def calc_medoid(self, points):
        centroid = self.calc_centroid(points)
        min_d = -1
        medoid = [-1,-1]
        for p in points:
            d = self.hubeny_distance(p, centroid)
            if d < min_d or min_d == -1:
                min_d = d
                medoid = p
        return medoid


    @classmethod
    def calc_centroid(self, points):
        xsum = sum([p[0] for p in points])
        ysum = sum([p[1] for p in points])
        return (xsum/len(points), ysum/len(points))

    @classmethod
    def calc_dispersion(self, points):
        c = self.calc_centroid(points)
        d = 0.0
        for p in points:
            d += self.hubeny_distance(c, p)
        return d / len(points)
    
    @classmethod
    def l2dist(self, p, q):
        if len(p) != len(q):
            return none
        s = 0.0
        psum = float(sum(p))
        qsum = float(sum(q))
        for i in range(0, len(p)):
            s += (p[i]/psum - q[i]/qsum)**2
        return s

    @classmethod
    def l2dist_fast(self, s, p, n, q):
        """ p is list, q is dict """
        for k, v in q.items():
            k = int(k)
            s -= p[k]**2
            s += (p[k] - v/n)**2
        return s

    @classmethod
    def kl_div_fast(self, p, n, q):
        s = 0.0
        for k, v in q.items():
            k = int(k)
            s += (v/n) * math.log((v/n)/p[k])
        return s

    
    @classmethod
    def rad(self, x):
        return x * math.pi / 180
    
    @classmethod
    def hubeny_distance(self, p, q):
        latd = self.rad(p[0] - q[0])
        longd = self.rad(p[1] - q[1])
        latm = self.rad(p[0] + q[0]) / 2
        a = 6377397.155
        b = 6356079.000
        e2 = 0.00667436061028297
        W = math.sqrt(1 - e2 * math.sin(latm)**2)
        M = 6334832.10663254 / W**3
        N = a / W
        d = math.sqrt((latd*M)**2 + (longd*N*math.cos(latm))**2)
        return d
    
    @classmethod
    def time_to_str(self, time_obj):
        return time_obj.strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def str_to_unixtime(self, time_str):
        time_obj = time.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        return int(time.mktime(time_obj))
