import math

def calc_centroid(points):
    xsum = sum([p[0] for p in points])
    ysum = sum([p[1] for p in points])
    return (xsum/len(points), ysum/len(points))

def rad(x):
    return x * math.pi / 180

def hubeny_distance(p, q):
    latd = rad(p[0] - q[0])
    longd = rad(p[1] - q[1])
    latm = rad(p[0] + q[0]) / 2
    a = 6377397.155
    b = 6356079.000
    e2 = 0.00667436061028297
    W = math.sqrt(1 - e2 * math.sin(latm)**2)
    M = 6334832.10663254 / W**3
    N = a / W
    d = math.sqrt((latd*M)**2 + (longd*N*math.cos(latm))**2)
    return d
