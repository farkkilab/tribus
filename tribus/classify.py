''' Start point of the command tribus classify '''
import numpy as np
import pandas as pd
from minisom import MiniSom

def somClustering(cells):
    '''run self-organized map to assign cells to nodes'''
    #TODO: choose clustering variables based on data length and width, number of labels in level and number of levels
    n=10
    sigma=0.3
    lr=0.5
    n_iterations=100
    som = MiniSom(n, n, sigma=sigma, learning_rate=lr)
    #TODO: cluster
    som.train(cells, n_iterations)
    #TODO: visualize clustering
    return(range(len(cells)))

# TODO: evaluate the weight and importance of each channel

def scoreNodes(nodes, rules):
    '''scoring function'''
    # save plots
    return('')

def assignLabels(scores):
    '''choose top label for each cell'''
    return('')

def processLevel(level):
    '''parallelize for samples if possible'''
    nodes = somClustering(cells)
    scores = scoreNodes(nodes, rules)
    labeled_data = assignLabels(scores)
    return(labeled_data)

def run(input,labels):
    levels = labels.keys()
    # how many levels of gates there are?
    for level in levels:
        processLevel(level)
    # concat results: data + level1 + level2 + level3 ...
    # return(results)

        
    