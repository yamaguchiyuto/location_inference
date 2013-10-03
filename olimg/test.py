import sys
import json
words = {}
for line in open(sys.argv[1], 'r'):
    lw = json.loads(line.rstrip())
    words[lw['word'].encode('utf8')] = lw['d']

for w, d in sorted(words.items(), key=lambda x:x[1]):
    print w,d
