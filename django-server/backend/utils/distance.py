from math import cos, sqrt, sin, radians

radius = 6378.1

def conv(x):
    p = (radians(x[0]), radians(x[1]))
    return radius * cos(p[0]) * cos(p[1]), radius * cos(p[0]) * sin(p[1]), radius * sin(p[0])

def euclidean(p1, p2):
    x1, y1, z1 = conv(p1)
    x2, y2, z2 = conv(p2) 
    
    return sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2) + (z1 - z2) * (z1 - z2))
