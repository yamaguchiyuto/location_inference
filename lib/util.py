def calc_centroid(points):
    xsum = sum([p[0] for p in points])
    ysum = sum([p[1] for p in points])
    return (xsum/len(points), ysum/len(points))
