from .create_zones import AMB_LOC
from .solution import Solution
import matplotlib.pyplot as plt

def tabuSearch(ambulanceLocs, zoneCenterLocs, count, numVehicles):
    # pre-calculate adjacency list
    adj = [[] for i in range(len(ambulanceLocs))]

    for loc in range(len(ambulanceLocs)):
        # find neighbours of this location
        row, col = loc // AMB_LOC, loc % AMB_LOC

        dx = [0, 0, 1, -1]
        dy = [-1, 1, 0, 0]

        for i in range(4):
            row2 = row + dx[i]
            col2 = col + dy[i]

            if 0 <= row2 and row2 < AMB_LOC and 0 <= col2 and col2 < AMB_LOC:
                adj[loc].append(row2 * AMB_LOC + col2)

        
    initialCnts = makeInitialSolution(ambulanceLocs, numVehicles)
    initialSolution = Solution(initialCnts, zoneCenterLocs, ambulanceLocs, count)
    bestSolution = Search(initialSolution, adj)

    lats_chosen = []
    longs_chosen = []

    for idx, cnt in enumerate(bestSolution.cnts):
        if cnt > 0:
            lats_chosen.append(ambulanceLocs[idx][0])
            longs_chosen.append(ambulanceLocs[idx][1])

    return [(lats_chosen[i], longs_chosen[i]) for i in range(len(lats_chosen))]


def makeInitialSolution(ambulanceLocs, numVehicles):
    N = len(ambulanceLocs) // numVehicles
    start = N // 2 - 1
    cnts = [0 for i in range(len(ambulanceLocs))]
    for i in range(numVehicles):
        cnts[start + i * N] = 1

    return cnts


def Search(currentSolution, adj):
    bestScore = currentSolution.evaluate()
    bestSolution = currentSolution 
    for i in range(10):
        print("Step: ", i)
        newSolution = currentSolution.generateBestNeighbour(adj)
        score = newSolution.evaluate()
        if score > bestScore:
            bestScore = score
            bestSolution = newSolution
        
        currentSolution = newSolution
        print(i, bestScore, bestSolution.countReachable(), bestSolution.demandCovered(), bestSolution.demandDoubleCovered())
    
    return bestSolution

