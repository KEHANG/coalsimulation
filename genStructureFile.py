PROBABLITY_BOND_BREAK = 0.5
PROBABLITY_BOND_REFORM = 0.2


#TODO TRY TO CODE FOR DIFFERENT STRUCTURES, like loop-shaped structure
#TODO THE FOLLOWING IS ONLY ONE STYLE
if __name__ == '__main__':
    bondLines = ''
    layerNum = 10
    breadth = 3
    currentLayerCluster = 2
    previousLayerCluster = 0
    for layer in range(layerNum):
        previousLayerCluster += 1
        for child in range(breadth):
            bondLines += str(previousLayerCluster) + ' ' + str(currentLayerCluster) + ' ' + \
                         str(PROBABLITY_BOND_BREAK) + ' ' + str(PROBABLITY_BOND_REFORM) + '\n'
            currentLayerCluster += 1
    file = open('structure2.txt', 'w')
    file.write(bondLines)