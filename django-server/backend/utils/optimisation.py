from create_zones import getZoneLocations, ZONE_LOC, AMB_LOC
from tabu_search import tabuSearch


# emergencyLocations -> list of tuples of form (latitude, longitude), numVehicles -> number of available vehicles
def getVehicleLocations(emergencyLocations, numVehicles):
    ambulanceLocs, zoneCenterLocs, count = getZoneLocations(emergencyLocations)
    chosenLocations = tabuSearch(ambulanceLocs, zoneCenterLocs, count, numVehicles)
    return chosenLocations
