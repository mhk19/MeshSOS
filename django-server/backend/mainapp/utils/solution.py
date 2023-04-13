from .distance import euclidean
from .search_params import *
import random
from copy import deepcopy

# Solution is an array denoting number of ambulances per chosen site
class Solution:
    def __init__(self, cnts, zoneCenterLocs, ambulanceLocs, count):
        self.cnts = cnts
        self.tabuDict = {}
        self.tabuSet = set()
        self.zoneCenterLocs = zoneCenterLocs
        self.ambulanceLocs = ambulanceLocs
        self.countZC = count
    
    def countReachable(self):
        currentLocs = []
        cntr = 0
        for j in range(len(self.cnts)):
            if self.cnts[j] > 0:
                currentLocs.append(j)

        for i in range(len(self.zoneCenterLocs)):
            reachable = False
            if self.countZC[self.zoneCenterLocs[i]] == 0:
                continue
            for loc in currentLocs:
                if euclidean(self.zoneCenterLocs[i], self.ambulanceLocs[loc]) <= LIM_UPPER:
                    reachable = True
            if reachable == True:
                cntr += 1
        
        return cntr

    def getMoveCandidates(self, adj, lower = False):
        violationList = []
        currentLocs = []
        for j in range(len(self.cnts)):
            if self.cnts[j] > 0:
                currentLocs.append(j)
            
        for i in range(len(self.zoneCenterLocs)):
            reachable = False
            if self.countZC[self.zoneCenterLocs[i]] == 0:
                continue
            for loc in currentLocs:
                if euclidean(self.zoneCenterLocs[i], self.ambulanceLocs[loc]) <= (LIM_LOWER if lower else LIM_UPPER) :
                    reachable = True
                    break
            if not reachable:
                violationList.append(i)
        
        toCandidates = set()
        moveCandidates = []
        for node in violationList:
            for i in range(len(self.ambulanceLocs)):
                if euclidean(self.zoneCenterLocs[node], self.ambulanceLocs[i]) <= (LIM_LOWER if lower else LIM_UPPER):
                    toCandidates.add(i)
        
        for candidate in toCandidates:
            for idx in adj[candidate]:
                if self.cnts[idx] > 0:
                    moveCandidates.append((idx, candidate))
        
        return moveCandidates

    def makeReachable(self, counter, adj):
        while True:
            if self.countReachable() == sum([0 if self.countZC[self.zoneCenterLocs[i]] == 0 else 1 for i in range(len(self.zoneCenterLocs))]):
                break
            if counter >= n_modifications:
                break

            # find best move
            moveCandidates = self.getMoveCandidates(adj)
            if len(moveCandidates) == 0:
                return counter

            bestMove, maxReach, idx = -1, 0, -1
            for fromNode, toNode in moveCandidates:
                idx += 1

                if (fromNode, toNode) in self.tabuSet:
                    continue

                self.cnts[toNode] += 1
                self.cnts[fromNode] -= 1

                reachableNodes = self.countReachable()
                if reachableNodes > maxReach:
                    bestMove = idx
                    maxReach = reachableNodes

                self.cnts[toNode] -= 1
                self.cnts[fromNode] += 1

            counter += 1
            self.removeTabu(counter)
            print("(Reachable) Counter = ", counter)

            # perform best move
            fromNode, toNode = moveCandidates[bestMove]
            self.addTabu(counter, (moveCandidates[bestMove][1], moveCandidates[bestMove][0]))
            self.cnts[toNode] += 1
            self.cnts[fromNode] -= 1
        
        return counter 
    

    def demandCovered(self):
        currentLocs = []
        totalDemand, coveredDemand = 0, 0
        for j in range(len(self.cnts)):
            if self.cnts[j] > 0:
                currentLocs.append(j)
        
        for i in range(len(self.zoneCenterLocs)):
            reachable = False
            if self.countZC[self.zoneCenterLocs[i]] == 0:
                continue
            for loc in currentLocs:
                if euclidean(self.zoneCenterLocs[i], self.ambulanceLocs[loc]) <= LIM_LOWER :
                    reachable = True
                    break
            if reachable:
                coveredDemand += self.countZC[self.zoneCenterLocs[i]]
            totalDemand += self.countZC[self.zoneCenterLocs[i]]
        
        return (coveredDemand / totalDemand)
    

    def demandDoubleCovered(self):
        currentLocs = []
        totalDemand, coveredDemand = 0, 0
        for j in range(len(self.cnts)):
            if self.cnts[j] > 0:
                currentLocs.append(j)
        
        for i in range(len(self.zoneCenterLocs)):
            countReach = 0
            if self.countZC[self.zoneCenterLocs[i]] == 0:
                continue
            for loc in currentLocs:
                if euclidean(self.zoneCenterLocs[i], self.ambulanceLocs[loc]) <= LIM_LOWER :
                    countReach += 1
                    if countReach == 2:
                        break
            if  countReach == 2:
                coveredDemand += self.countZC[self.zoneCenterLocs[i]]
            totalDemand += self.countZC[self.zoneCenterLocs[i]]
        

        return (coveredDemand / totalDemand)

    def removeTabu(self, counter):
        if counter not in self.tabuDict.keys():
            return

        for ele in self.tabuDict[counter]:
            if ele in self.tabuSet:     # TODO: why was this necessary
                self.tabuSet.remove(ele)
        del self.tabuDict[counter]
    
    def addTabu(self, counter, ele):
        self.tabuSet.add(ele)
        removeTime = counter + random.randint(tabu_low, tabu_high)
        if removeTime in self.tabuDict.keys():
            self.tabuDict[removeTime].append(ele)
        else:
            self.tabuDict[removeTime] = [ele]

    def makeAlpha(self, counter, adj):
        while True:
            if self.demandCovered() >= alpha:
                break

            if counter >= n_modifications:
                break
            
            bestMove, maxCovered, idx = -1, 0, -1
            moveCandidates = self.getMoveCandidates(adj, True) 

            if len(moveCandidates) == 0:        # TODO: why was this if case necessary, should not be??
                return counter

            for fromNode, toNode in moveCandidates:
                idx += 1

                if (fromNode, toNode) in self.tabuSet:
                    continue

                self.cnts[toNode] += 1
                self.cnts[fromNode] -= 1

                coverage = self.demandCovered()
                if coverage > maxCovered:
                    maxCovered = coverage
                    bestMove = idx
                
                self.cnts[fromNode] += 1
                self.cnts[toNode] -= 1

            counter += 1

            self.removeTabu(counter)

            print("(Alpha) Counter = ", counter)

            # perform best move
            fromNode, toNode = moveCandidates[bestMove]
            self.addTabu(counter, (moveCandidates[bestMove][1], moveCandidates[bestMove][0]))
            self.cnts[toNode] += 1
            self.cnts[fromNode] -= 1

        return counter

    def generateOneNeighbour(self, adj):
        # print("here")
        newSol = Solution(self.cnts, self.zoneCenterLocs, self.ambulanceLocs, self.countZC) 
        counter = 0
        indices = [i for i in range(len(self.cnts))]
        random.shuffle(indices)

        done = False
        for idx in indices:
            if self.cnts[idx] > 0:
                # an ambulance is placed at current node
                neighbourList = adj[idx]
                random.shuffle(neighbourList)

                for x in neighbourList:
                    # check if x can accomodate more ambulances
                    if self.cnts[x] < AMB_LIM:
                        newSol.cnts[x] += 1
                        newSol.cnts[idx] -= 1
                        done = True
                        break 
                
                if done:
                    break
        
        if not done:
            return newSol
        else:
            while True:
                old_counter = counter

                counter = newSol.makeReachable(counter, adj)
                counter = newSol.makeAlpha(counter, adj)
                
                print("Counter = ", counter)

                if counter == old_counter or counter >= n_modifications:
                    break

            # TODO: add greedy improving steps as per research paper

            if counter < n_modifications:
                newSol
            return newSol

    def evaluate(self):
        # score = 2 * self.countReachable() + 1.5 * min(alpha, self.demandCovered()) + self.demandDoubleCovered()
        score = -2 * self.countReachable() - 1.5 * min(alpha, self.demandCovered()) + self.demandDoubleCovered()  # This is the function from research paper, why minus signs??
        return score

    def generateBestNeighbour(self, adj):
        neighbourSols = [self.generateOneNeighbour(adj) for i in range(neighbourhood_size)]
        bestScore = 0
        bestSolution = neighbourSols[0]
        for solution in neighbourSols:
            score = solution.evaluate()
            if score > bestScore:
                bestScore = score
                bestSolution = solution
        
        return bestSolution
