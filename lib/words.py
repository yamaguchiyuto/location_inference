# -*- coding: utf-8 -*-
import json

class Words:
    def __init__(self, words={}):
        self.values = words

    def __str__(self):
        res = ""
        for word in self.values.values():
            res += json.dumps(word) + "\n"
        return res[:-1]

    def set(self, words):
        self.values = words

    def load_file(self, filepath):
        for line in open(filepath, 'r'):
            word = json.loads(line.rstrip())
            self.values[word['word']] = word
    
    def load_mysql(self, mysqldb):
        pass

    def load_mongodb(self, mongodb):
        pass
    
    def get(self, word_str):
        if word_str in self.values:
            return self.values[word_str]
        else:
            return None

    def contain(self, w):
        if w in self.values:
            return True
        else:
            return False

    def add(self, word):
        if not word['word'] in self.values:
            self.values[word['word']] = word

    def iter(self):
        for word in self.values.values():
            yield word 

if __name__ == '__main__':
    import sys

    words = Words()
    words.load_file(sys.argv[1])
    print words.get(u'那覇')
    print words.get(u'北浦和')
