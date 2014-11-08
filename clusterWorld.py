import random
import math
from genStructureFile import PROBABLITY_BOND_BREAK, PROBABLITY_BOND_REFORM

seedNum = 0
random.seed(seedNum)


def breakingProbByLeavingGroupSize(leavingGroupSize):
    return PROBABLITY_BOND_BREAK/(1.1**leavingGroupSize)

class Cluster(object):
    def __init__(self, name):
        self.name = str(name)
    def getName(self):
        return self.name
    def __str__(self):
        return self.name
    def __repr__(self):
        return self.name
    def __eq__(self, other):
        return self.name == other.name
    def __ne__(self, other):
        return not self.__eq__(other)
    def __hash__(self):
        # Override the default hash method
        # Think: Why would we want to do this?
        return self.name.__hash__()

class Bond(object):
    def __init__(self, src, dest):
        self.src = src
        self.dest = dest
    def getSource(self):
        return self.src
    def getDestination(self):
        return self.dest
    def __str__(self):
        return '{0}->{1}'.format(self.src, self.dest)

class Digraph(object):
    """
    A directed graph
    """
    def __init__(self):
        # A Python Set is basically a list that doesn't allow duplicates.
        # Entries into a set must be hashable (where have we seen this before?)
        # Because it is backed by a hashtable, lookups are O(1) as opposed to the O(n) of a list (nifty!)
        # See http://docs.python.org/2/library/stdtypes.html#set-types-set-frozenset
        self.clusters = set([])
        self.bonds = {}
        self.potentialReformBonds = {}

    def getClusterNum(self):
        return len(self.clusters)

    def addCluster(self, cluster):
        if cluster in self.clusters:
            # Even though self.nodes is a Set, we want to do this to make sure we
            # don't add a duplicate entry for the same node in the self.edges list.
            raise ValueError('Duplicate cluster')
        else:
            self.clusters.add(cluster)
            self.bonds[cluster] = set([])
            self.potentialReformBonds[cluster] = []

    def addBond(self, bond):
        src = bond.getSource()
        dest = bond.getDestination()

        if not(src in self.clusters and dest in self.clusters):
            raise ValueError('Cluster not in graph')

        if (dest not in self.bonds[src]) and (src not in self.bonds[dest]):
            self.bonds[src].add(dest)
            self.bonds[dest].add(src)
        else:
            raise ValueError('Bond: {0} already exists!'.format(bond.str()))

    def childrenOf(self, cluster):
        return self.bonds[cluster]

    def hasCluster(self, cluster):
        return cluster in self.clusters

    def __str__(self):
        res = ''
        for k in self.clusters:
            for d in self.bonds[k]:
                res = '{0}{1}->{2}\n'.format(res, k, d)
        return res[:-1]

class BondInfo(object):
    # mainly used for bondtuple to collect all the info associated with the bond
    def __init__(self, breakProb = PROBABLITY_BOND_BREAK, reformProb = PROBABLITY_BOND_REFORM):
        self.breakProb = breakProb
        self.reformProb = reformProb

    def setBreakProb(self, breakProb):
        self.breakProb = breakProb

    def setReformProb(self, reformingProb):
        self.reformProb = reformingProb

    def getBreakProb(self):
        return self.breakProb

    def getReformProb(self):
        return self.reformProb

class WeightedBond(Bond):
    def __init__(self, src, dest, bondInfo):
        Bond.__init__(self, src, dest)
        self.bondInfo = bondInfo

    def getProbBondBreak(self):
        return self.bondInfo.getBreakProb()

    def getProbBondReform(self):
        return self.bondInfo.getReformProb()

    def __str__(self):
        return Bond.__str__(self) + ' ({0}, {1})'.format(self.getProbBondBreak(), self.getProbBondReform())



class WeightedDigraph(Digraph):

    def childrenOf(self, cluster):
        children = set([])
        for d in self.bonds[cluster]:
            children.add(d[0])
        return children

    def getMaxConnectedClusterGroupWith(self, cluster, clusterSet = set([])):
        clusterSet.add(cluster)
        if self.childrenOf(cluster).issubset(clusterSet):
            return clusterSet

        for child in self.childrenOf(cluster):
            if child in clusterSet:
                continue
            else:
                clusterSet.union(self.getMaxConnectedClusterGroupWith(child, clusterSet))

        return clusterSet

    def getMaxConnectedClusterGroupWithThisWithoutThat(self, clusterThis, clusterThat, clusterSet = set([])):
        # this method is mainly to calculate the maxConnectedClusterGroup suppose bond (this --> that) is broken
        clusterSet.add(clusterThis)
        if self.childrenOf(clusterThis).issubset(clusterSet):
            return clusterSet

        for child in self.childrenOf(clusterThis):
            if child in clusterSet or child == clusterThat:
                continue
            else:
                clusterSet.union(self.getMaxConnectedClusterGroupWith(child, clusterSet))

        return clusterSet

    def isCompleteDigraph(self):
        cluster = next(iter(self.clusters))
        clusterSet = self.getMaxConnectedClusterGroupWith(cluster, set([]))

        return clusterSet == self.clusters

    def hasDestInBondsOfSrc(self, src, dest):
        for bondTuple in self.bonds[src]:
            if dest == bondTuple[0]:
                return True
        return False

    def hasDestInPotentialReformBondsOfSrc(self, src, dest):
        for bondTuple in self.potentialReformBonds[src]:
            if dest == bondTuple[0]:
                return True
        return False

    def removeDestFromBondsOfSrc(self, src, dest):
        bondTupleToRemove = None
        for bondTuple in self.bonds[src]:
            if dest == bondTuple[0]:
                bondTupleToRemove = bondTuple
                break
        if bondTupleToRemove != None:
            self.bonds[src].remove(bondTupleToRemove)

    def removeDestFromPotentialReformBondsOfSrc(self, src, dest):
        bondTupleToRemove = None
        for bondTuple in self.potentialReformBonds[src]:
            if dest == bondTuple[0]:
                bondTupleToRemove = bondTuple
                break
        if bondTupleToRemove != None:
            self.potentialReformBonds[src].remove(bondTupleToRemove)


    def addBond(self, bond):
        src = bond.getSource()
        dest = bond.getDestination()

        if not(src in self.clusters and dest in self.clusters):
            raise ValueError('Cluster not in graph')

        if (not self.hasDestInBondsOfSrc(src, dest)) and (not self.hasDestInBondsOfSrc(dest, src)):
            probBondBreak = bond.getProbBondBreak()
            probBondReform = bond.getProbBondReform()
            bondInfo = BondInfo()
            bondInfo.setBreakProb(probBondBreak)
            bondInfo.setReformProb(probBondReform)
            self.bonds[src].add((dest,bondInfo))
            self.bonds[dest].add((src,bondInfo))
        else:
            raise ValueError('Bond: {0} already exists!'.format(str(bond)))

    # not used in initialization but after bond removal
    # potentialReformBond is always the bond just removed
    def addPotentialReformBond(self, potentialReformBond):
        src = potentialReformBond.getSource()
        dest = potentialReformBond.getDestination()


        if not(src in self.clusters):
            raise ValueError('Cluster not in graph')

        if not self.hasDestInPotentialReformBondsOfSrc(src, dest):
            probBondBreak = potentialReformBond.getProbBondBreak()
            probBondReform = potentialReformBond.getProbBondReform()
            bondInfo = BondInfo()
            bondInfo.setBreakProb(probBondBreak)
            bondInfo.setReformProb(probBondReform)
            self.potentialReformBonds[src].append((dest,bondInfo))
            self.potentialReformBonds[dest].append((src,bondInfo))
        else:
            raise ValueError('Potential Reform Bond: {0} already exists!'.format(str(potentialReformBond)))

    def addPotentialReformBondList(self, potentialReformBondList):
        for potentialReformBond in potentialReformBondList:
            self.addPotentialReformBond(potentialReformBond)


    def removePotentialReformBond(self, potentialReformBond):
        # this method is used only after
        # potential reform bond has been reformed
        src = potentialReformBond.getSource()
        dest = potentialReformBond.getDestination()
        # breakProb = potentialReformBond.getProbBondBreak()
        # reformPorb = potentialReformBond.getProbBondReform()

        # the src and dest potentialReformBond can be
        # both in the current digraph
        # also possibly only one of them in
        # but not possible if both not in
        srcIn = self.hasCluster(src)
        destIn =self.hasCluster(dest)
        if srcIn:
            if self.hasDestInPotentialReformBondsOfSrc(src, dest):
                self.removeDestFromPotentialReformBondsOfSrc(src, dest)
            else:
                raise ValueError("Potential Reform Bond: {0} doesn't exist!".format(str(potentialReformBond)))
        if destIn:
            if self.hasDestInPotentialReformBondsOfSrc(dest, src):
                self.removeDestFromPotentialReformBondsOfSrc(dest, src)
            else:
                raise ValueError("Potential Reform Bond: {0} doesn't exist!".format(str(potentialReformBond)))

        if not(srcIn and destIn):
            raise ValueError('Cluster not in graph')

    def removeBond(self, bondToRemove):
        src = bondToRemove.getSource()
        dest = bondToRemove.getDestination()
        if not(src in self.clusters and dest in self.clusters):
            raise ValueError('Cluster not in graph')

        if self.hasDestInBondsOfSrc(src, dest):
            self.removeDestFromBondsOfSrc(src, dest)
            self.removeDestFromBondsOfSrc(dest, src)
        else:
            raise ValueError("Bond: {0} doesn't exist!".format(str(bondToRemove)))

    def removeBondList(self, bondListToRemove):
        for bondToRemove in bondListToRemove:
            self.removeBond(bondToRemove)

    def genRemoveBondList(self):
        # return a bondList consist of bonds to remove by probability
        removeBondList = []
        for cluster1 in self.clusters:
            for bondTuple in self.bonds[cluster1]:
                cluster2 = bondTuple[0]
                if cluster1.getName() > cluster2.getName():
                    rand = random.random()
                    bondInfo = bondTuple[1]
                    breakProb = bondInfo.getBreakProb()
                    if rand < breakProb:
                        bondToRemove = WeightedBond(cluster1, cluster2, bondInfo)
                        removeBondList.append(bondToRemove)
        return removeBondList

    def genReformBondList(self):
        # return a bondList consist of bonds to reform by probability
        # all the bonds has src in the current digraph
        # while dest not surely in the current digraph
        reformBondList = []
        for cluster1 in self.clusters:
            for bondTuple in self.potentialReformBonds[cluster1]:
                cluster2 = bondTuple[0]
                if cluster1.getName() > cluster2.getName():
                    rand = random.random()
                    bondInfo = bondTuple[1]
                    reformProb = bondInfo.getReformProb()
                    if rand < reformProb:
                        bondToReform = WeightedBond(cluster1, cluster2, bondInfo)
                        reformBondList.append(bondToReform)
        return reformBondList


    def calcBreakingProb(self, bond, breakingProbFunc = breakingProbByLeavingGroupSize):

        # get the size of leaving group containing src cluster and dest cluster respectvely
        src = bond.getSource()
        dest = bond.getDestination()

        srcGroupSize = len(self.getMaxConnectedClusterGroupWithThisWithoutThat(src, dest, set([])))
        graphClusterNum = self.getClusterNum()

        if srcGroupSize == graphClusterNum:
            destGroupSize = srcGroupSize
        else:
            destGroupSize = graphClusterNum - srcGroupSize

        # define leaving size and calculate the breaking probability based on the size
        leavingGroupSize = min(srcGroupSize, destGroupSize)
        breakingProb = breakingProbFunc(leavingGroupSize)

        return breakingProb


    def updateBreakingProbForEachBond(self):
        for src in self.clusters:
            for bondTuple in self.bonds[src]:
                dest = bondTuple[0]
                bondInfo = bondTuple[1]
                # to calculate breakProb it's not necessary to know previous bondinfo
                bond = Bond(src, dest)
                newBreakingProb = self.calcBreakingProb(bond)
                bondInfo.setBreakProb(newBreakingProb)

    def __str__(self):
        res = ''
        for k in self.bonds:
            for d in self.bonds[k]:
                res = '{0}{1}->{2} ({3})\n'.format(res, k, d[0], d[1].getBreakProb())
        return res[:-1]

class World(object):
    def __init__(self, filename):
        self.digraphs = []
        self.filename = filename

    def getDigraphNum(self):
        return len(self.digraphs)

    def getClusterNumList(self):
        clusterNumList = []
        self.updateDigraphs()
        for digraph in self.digraphs:
            clusterNumList.append(digraph.getClusterNum())
        return clusterNumList

    def getHistogram(self, clusterNumList):
        import pylab
        pylab.figure('Histogram for ClusterNumberList')
        pylab.hist(clusterNumList)
        pylab.show()

    def loadDigraph(self):
        file = open(self.filename, 'r', 0)
        weightedDigraph = WeightedDigraph()
        for line in file:
            lineSplit = line.split(' ')
            src = Cluster(lineSplit[0])
            dest = Cluster(lineSplit[1])
            breakProb = float(lineSplit[2])
            reformProb = float(lineSplit[3])
            bondInfo = BondInfo(breakProb = breakProb, reformProb = reformProb)
            bond = WeightedBond(src, dest, bondInfo)

            # add src and dest two clusters
            if not weightedDigraph.hasCluster(src):
                weightedDigraph.addCluster(src)

            if not weightedDigraph.hasCluster(dest):
                weightedDigraph.addCluster(dest)

            weightedDigraph.addBond(bond)
        return [weightedDigraph]

    def addDigraph(self, digraph):
        self.digraphs.append(digraph)

    def updateDigraphs(self):
        newDigraphs = []
        for digraph in self.digraphs:
            # subgraphCounter = 1
            while not digraph.isCompleteDigraph():
                cluster = next(iter(digraph.clusters))
                clusterSet = digraph.getMaxConnectedClusterGroupWith(cluster,set([]))

                # print('Checking cluster"s maxCG: Cluster ' + str(cluster))
                # print(clusterSet)
                # subgraphCounter += 1
                # print("subgraphCounter: " + str(subgraphCounter))


                clusterList = list(clusterSet)
                # create new graph
                newDigraph = WeightedDigraph()
                # add clusters to newDigraph
                for cluster in clusterList:
                    newDigraph.addCluster(cluster)
                # subtract clusters from original digraph
                digraph.clusters = digraph.clusters.difference(clusterSet)

                # print("original digraph.cluster")
                # print(digraph.clusters)

                # add bonds for newDigraph and delete bonds for original ones
                for cluster in clusterList:
                    newDigraph.bonds[cluster] = set(digraph.bonds[cluster])
                    del digraph.bonds[cluster]

                    newDigraph.potentialReformBonds[cluster] = list(digraph.potentialReformBonds[cluster])
                    del digraph.potentialReformBonds[cluster]
                # print("New digraph: ")
                # print(str(newDigraph))
                # print("Original digraph: ")
                # print(str(digraph))
                newDigraphs.append(newDigraph)
            newDigraphs.append(digraph)
        self.digraphs = newDigraphs

    # used when some bond is reformed
    def combineGraphs(self, bondListToCombineGraphs):

        for bondToCombineGraphs in bondListToCombineGraphs:
            src = bondToCombineGraphs.getSource()
            dest = bondToCombineGraphs.getDestination()
            srcGraph = None
            destGraph = None
            # combinedGraph = None
            combinedGraph = WeightedDigraph()
            for digraph in self.digraphs:
                if digraph.hasCluster(src):
                    srcGraph = digraph
                if digraph.hasCluster(dest):
                    destGraph = digraph
                if (srcGraph != None) and (destGraph != None):
                    break

            if srcGraph != destGraph:
                clustersUnion = srcGraph.clusters.union(destGraph.clusters)
                for cluster in clustersUnion:
                    combinedGraph.addCluster(cluster)
                    if srcGraph.hasCluster(cluster):
                        combinedGraph.bonds[cluster] = set(srcGraph.bonds[cluster])
                        combinedGraph.potentialReformBonds[cluster] = list(srcGraph.potentialReformBonds[cluster])
                    else:
                        combinedGraph.bonds[cluster] = set(destGraph.bonds[cluster])
                        combinedGraph.potentialReformBonds[cluster] = list(destGraph.potentialReformBonds[cluster])

                self.digraphs.append(combinedGraph)
                self.digraphs.remove(srcGraph)
                self.digraphs.remove(destGraph)

            else:
                combinedGraph = srcGraph

            # add bond to src&dest in combinedGraph
            # and remove potentialReformBond for src&dest in combinedGraph
            combinedGraph.addBond(bondToCombineGraphs)
            combinedGraph.removePotentialReformBond(bondToCombineGraphs)

    def singleSimulation(self, steps, updateBreakProb = True):
        self.digraphs = self.loadDigraph()
        for step in range(steps):
            bondListToCombineGraphs = []
            for digraph in self.digraphs:

                # generate removal bond list for each graph in world
                # every time before generating removal bonds
                # should update the breaking probability
                if updateBreakProb == True:
                    digraph.updateBreakingProbForEachBond()
                bondListToRemove = digraph.genRemoveBondList()

                # generate reform bond list for each graph in world
                bondListToReform = digraph.genReformBondList()

                digraph.removeBondList(bondListToRemove)
                digraph.addPotentialReformBondList(bondListToRemove)

                for bondToReform in bondListToReform:
                    src = bondToReform.getSource()
                    dest = bondToReform.getDestination()
                    # if src and dest of bondToReform are both
                    # in the current digraph do reforming
                    if digraph.hasCluster(src) and digraph.hasCluster(dest):
                        digraph.addBond(bondToReform)
                        digraph.removePotentialReformBond(bondToReform)
                    else:
                        # if src is in while dest is out,
                        # collect the bond and
                        # do the reforming in updateDigraphs()
                        bondListToCombineGraphs.append(bondToReform)

            self.updateDigraphs()
            print('after updating digraphs: ')
            for digraph in self.digraphs:
                print str(digraph)
            self.combineGraphs(bondListToCombineGraphs)
            if len(bondListToCombineGraphs) != 0:
                print('after combining digraphs: ')
                for digraph in self.digraphs:
                    print str(digraph)

            print('World has digraphs: ')
            print(self.getDigraphNum())

        print('Single Simulation Done!')
        clusterNumList = self.getClusterNumList()
        clusterNum_range = range(min(clusterNumList),1+max(clusterNumList))
        frequencies = [clusterNumList.count(i) for i in clusterNum_range]
        print(clusterNum_range)
        print(frequencies)
        self.getHistogram(self.getClusterNumList())


    #TODO Consider reform prob update
    #TODO Visualize the whole process

