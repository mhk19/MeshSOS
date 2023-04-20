from .create_zones import getZoneLocations, ZONE_LOC, AMB_LOC
from .tabu_search import tabuSearch
from .distance import euclidean
from scipy.optimize import linear_sum_assignment
from datetime import datetime

# locationAndTimeData -> list of tuples of form (latitude, longitude, timestamp), timestamp format: "%Y-%m-%d %H:%M:%S"
# return 2D list where list[i][j] -> the location of the ith vehicle for the jth period in the day
# len(list) = numVehicles | len(list[i]) = 4 for every i   

def getVehicleRoutes(locationAndTimeData, numVehicles):
    # Morning -> (6 AM - 12 noon)
    # Afternoon -> (12 noon - 6 PM)
    # Evening -> (6 PM - 12 midnight)
    # Night -> (12 midnight - 6 AM)
    emergencyLocationLists = [list() for i in range(4)]   # List of 4 empty lists
    for data in locationAndTimeData:
        ts = datetime.strptime(data[2], "%Y-%m-%d %H:%M:%S")
        hour = int(ts.hour)
        emergencyLocationLists[hour // 6].append((float(data[0]), float(data[1])))

    ambulanceLocationLists = [getVehicleLocations(emergencyLocationLists[i], numVehicles) for i in range(4)]

    ambulanceRoutes = [[ambulanceLocationLists[0][i]] for i in range(numVehicles)]

    for i in range(1, 4):
        matches, maxTravel = getRoute(ambulanceLocationLists[i-1], ambulanceLocationLists[i])
        for j in range(numVehicles):
            for k in range(len(matches)):
                if ambulanceRoutes[j][-1] == matches[k][0]:
                    ambulanceRoutes[j].append(matches[k][1])
                    break
    
    return ambulanceRoutes

# emergencyLocations -> list of tuples of form (latitude, longitude), numVehicles -> number of available vehicles
def getVehicleLocations(emergencyLocations, numVehicles):
    ambulanceLocs, zoneCenterLocs, count = getZoneLocations(emergencyLocations)
    chosenLocations = tabuSearch(ambulanceLocs, zoneCenterLocs, count, numVehicles)
    return chosenLocations

def getRoute(initialPositions, finalPositions, maxTravel = 5):
    n = len(initialPositions)
    infty = n * 1000000
    if len(finalPositions) != n:
        raise Exception("Number of new and old locations do not match!!")
    
    while True:
        costArray = []
        for i in range(n):
            costs = []
            for j in range(n):
                dist = euclidean(initialPositions[i], finalPositions[j])
                costs.append(dist if dist <= maxTravel else infty)
            costArray.append(costs)
        
        fromIndices, toIndices = linear_sum_assignment(costArray)

        totalCost = 0
        for i in range(len(fromIndices)):
            totalCost += costArray[fromIndices[i]][toIndices[i]]
        
        if totalCost < infty:
            matches = [(initialPositions[fromIndices[i]], finalPositions[toIndices[i]]) for i in range(len(fromIndices))]
            return matches, maxTravel
        else:
            maxTravel += 1