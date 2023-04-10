## Usage

The main script is **optimisation.py**. It contains the following functions:

1. ***getVehicleLocation(emergencyLocations, numVehicles)***

- *emergencyLocations:* List of tuples of the emergency locations in the form *(latitude, longitude)*
- *numVehicles:* Number of vehicles available to place

    Returns *chosenLocations*, a list of tuples of the form *(latitude, longitude)*.

2. ***getRoutes(initialLocations, finalLocations, maxTravel = 5)***

- *initialLocations:* List of tuples of the initial vehicle locations in the form *(latitude, longitude)*
- *finalLocations:* List of tuples of the final vehicle locations in the form *(latitude, longitude)*
- *maxTravel:* Maximum distance that a vehicle may travel between the two locations

    Returns two values:
    - *movements:* List of tuple of tuples in the format *((initialLatitude, initialLongitude), (finalLatitude, finalLongitude))*
    - *maxTravelActual:* Maximum of *maxTravel* and the actual maximum distance travelled.

**Note:** getRoutes tries to achieve *maxTravel* but it does not guarantee. It increases *maxTravel* by 1 till it becomes possible and returns the final value as *maxTravelActual*.

3. ***getVehicleLocation_kMedoids(emergencyLocations, numVehicles)***

- Same as *getVehicleLocation(emergencyLocations, numVehicles)*, uses K-medoids instead of Tabu Search to generate answers.