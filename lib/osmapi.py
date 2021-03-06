# -*- coding: utf-8 -*-
import urllib
import json

class OsmApi:
    def __init__(self):
        self.url = "http://nominatim.openstreetmap.org/search"
        self.format = "json"
    
    def get(self, q):
        url = self.url + '?' + 'q="%s"' % q + '&format=%s' % self.format
        f = urllib.urlopen(url)
        obj = json.loads(f.read())
        if len(obj) > 0:
            return obj[0]
        else:
            return None

if __name__ == '__main__':
    client = OsmApi()
    obj = client.get('東京タワー')
    print obj
    obj = client.get('a')
    print obj
