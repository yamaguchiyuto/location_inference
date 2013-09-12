from util import Util


a = [1,3,1,3,1,3,4,5]
s = float(sum(a))
for i in range(0, len(a)):
    a[i] = a[i] / s
s = sum([v**2 for v in a])

print s
b = {3:1, 5:9}
c = [0,0,0,1,0,9,0,0]

print Util.l2dist(a,c)
Util.l2dist_fast(s, a,b)

print s

