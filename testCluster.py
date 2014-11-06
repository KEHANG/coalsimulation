from clusterWorld import *

seedNum = 6
random.seed(seedNum)

file1 = 'structure.txt'
file2 = 'structureNoReform.txt'
file3 = 'structure3.txt'
file4 = 'structure4.txt'

def testGetMaxConnectedClusterGroupWithThisWithoutThat():
    world = World(file1)
    world.digraphs = world.loadDigraph()
    for graph in world.digraphs:
        clusterThis = Cluster('6')
        clusterThat = Cluster('8')
        print('It should print: 1')
        print(len(graph.getMaxConnectedClusterGroupWithThisWithoutThat(clusterThis, clusterThat, set([]))))

# testGetMaxConnectedClusterGroupWithThisWithoutThat()

def testCalcBreakingProb():
    world = World(file1)
    world.digraphs = world.loadDigraph()
    for graph in world.digraphs:
        clusterThis = Cluster('1')
        clusterThat = Cluster('2')
        bond = Bond(clusterThis, clusterThat)
        print('It should print: 0.310')
        print(graph.calcBreakingProb(bond))

# testCalcBreakingProb()

def testUpdateBreakingProbForEachBond():
    world = World(file1)
    world.digraphs = world.loadDigraph()
    for graph in world.digraphs:
        print(graph)
        graph.updateBreakingProbForEachBond()
        print(graph)

# testUpdateBreakingProbForEachBond()