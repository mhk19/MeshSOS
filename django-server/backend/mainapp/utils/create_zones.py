from .distance import euclidean
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

AMB_LOC = 30
ZONE_LOC = 120

def populate(arr, LOC_COUNT, top_left, bottom_left, zoneLats, zoneLngs, d_ew, d_ns, zones = False):
    diff_ew = d_ew / LOC_COUNT
    diff_ns = d_ns / LOC_COUNT

    for i in range(LOC_COUNT):
        if zones:
            zoneLats.append(bottom_left[0] + diff_ns / 2 + diff_ns * i)
        for j in range(LOC_COUNT):
            arr.append((bottom_left[0] + diff_ns / 2 + diff_ns * i, top_left[1] + diff_ew / 2 + diff_ew * j))
            if zones and i == 0:
                zoneLngs.append(bottom_left[1] + diff_ew / 2 + diff_ew * j)

def getLowerBound(arr, val, idx):
    if val < arr[0]:
        return arr[0]
    
    st, en = 0, len(arr)-1
    best = 0
    while st <= en:
        mid = (st + en)//2
        if arr[mid] <= val:
            st = mid+1
            best = mid
        else:
            en = mid-1
    
    return arr[best]

def getZoneLocations(emergencyLocations):
    latitudes = [emergencyLocations[i][0] for i in range(len(emergencyLocations))]
    longitudes = [emergencyLocations[i][1] for i in range(len(emergencyLocations))]

    latitudes = np.array(latitudes)
    longitudes = np.array(longitudes)
    
    lati_range = (latitudes.min(), latitudes.max())
    longi_range = (longitudes.min(), longitudes.max())

    top_left = (lati_range[1], longi_range[0])
    top_right = (lati_range[1], longi_range[1])
    bottom_left = (lati_range[0], longi_range[0])
    bottom_right = (lati_range[0], longi_range[1])

    d_ew = longi_range[1] - longi_range[0]
    d_ns = lati_range[1] - lati_range[0]

    
    ambulanceLocs = []
    zoneCenterLocs = []

    zoneLats = []
    zoneLngs = []
    
    populate(ambulanceLocs, AMB_LOC, top_left, bottom_left, zoneLats, zoneLngs, d_ew, d_ns)
    populate(zoneCenterLocs, ZONE_LOC, top_left, bottom_left, zoneLats, zoneLngs, d_ew, d_ns, True)

        
    count = {}

    for loc in zoneCenterLocs:
        count[loc] = 0
        
    xs = []
    ys = []

    for index, (x, y) in enumerate(emergencyLocations):
        xs.append(x)
        ys.append(y)

        # get closest zone center to (x, y)
        zx = getLowerBound(zoneLats, x, index)
        zy = getLowerBound(zoneLngs, y, index)


        # print(x, y, zx, zy)

        if (zx, zy) not in count.keys():
            assert False        # SANITY CHECK: control should never reach here
        else:
            count[(zx, zy)] += 1
    
    return ambulanceLocs, zoneCenterLocs, count












