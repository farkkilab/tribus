''' Start point of the command tribus classify '''

def somClustering(cells):
    '''run self-organized map to assign cells to nodes'''
    #TODO: choose clustering variable based on data length and width
    #TODO: cluster
    #TODO: visualize clustering
    return(range(len(cells)))

def scoreNodes(nodes, rules):
    '''scoring function'''
    # save plots
    return('')

#assign
def assignLabels(scores):
    '''choose top label for each cell'''
    return('')

def processLevel():
    '''parallelize for samples if possible'''
    nodes = somClustering(cells)
    scores = scoreNodes(nodes, rules)
    labeled_data = assignLabels(scores)
    return(labeled_data)

def run(input,labels):
    print(input)
    print(labels)
    # how many levels of gates there are?
    for level in labels_set:
        processLevel(level)
    # concat results: data + level1 + level2 + level3 ...
    # return(results)

        
    