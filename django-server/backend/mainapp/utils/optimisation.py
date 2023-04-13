from .create_zones import getZoneLocations, ZONE_LOC, AMB_LOC
from .tabu_search import tabuSearch
from .distance import euclidean
from scipy.optimize import linear_sum_assignment

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