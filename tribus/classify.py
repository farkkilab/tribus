''' Start point of the command tribus classify '''
import numpy as np
import pandas as pd
from minisom import MiniSom
from sklearn_som.som import SOM
from FlowGrid import *
import os

def clusterCells(cells):
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

# TODO: function evaluate the weight and importance of each channel in the clustering result

def scoreNodes(nodes, rules):
    '''scoring function'''
    # save plots
    return('')

def assignLabels(scores):
    '''choose top label for each cell'''
    return('')

def processLevel(level):
    '''parallelize for samples if possible'''
    # TODO PARALLELIZE HERE

    #nodes = somClustering(cells)
    #scores = scoreNodes(nodes, rules)
    #labeled_data = assignLabels(scores)
    #return(labeled_data)
    return('')

def score_marker_pos(x):
    res = [ (np.percentile(x, 95) - i)**2 for i in x]
    return res

def score_marker_neg(x):
    res = [ (i - np.min(x))**2 for i in x]
    return res

def normalize_scores(x):
    res = 1 - ((x - np.min(x)) / (np.max(x) - np.min(x)))
    return res

def run(input_path,labels,output_folder):
    levels = list(labels.keys())

    # Read data
    filenames=os.listdir(input_path) 

    samplefile=filenames[0]
    
    #for samplefile in filenames:
    sample_data=pd.read_csv(os.path.join(input_path,samplefile))
        #for level in levels:
    level = levels[0]
    # Test if the gating needs columns that don't exist: TODO only channels with non-zero values!
    if  set(sample_data.columns.values).issubset(set(labels[level].index.values)):
        # return some error
        print(labels[level].index.values)
        print(sample_data.columns.values)
        return("ERROR: gating columns missing")
    # Filter table to have only the correct channels
    level_logic_df = labels[level]

    test_data = sample_data[labels[level].index.values].to_numpy()
    test_som = SOM(m=5, n=5, dim=6)
    test_som.fit(test_data)
    predictions = test_som.predict(test_data)
    print("som labels")
    unique, counts = np.unique(predictions, return_counts=True)
    print(dict(zip(unique, counts)))

    # For each node calculate median expression of each gating marker
    data_to_score = 

    
    scores_matrix = np.zeros((sample_data.shape[0], labels[level].shape[1]))
    for idx, cell_type in enumerate(labels[level].columns.values):
        print(cell_type)
        list_negative = list(level_logic_df.loc[level_logic_df[cell_type] == -1].index)
        list_positive = list(level_logic_df.loc[level_logic_df[cell_type] == 1].index)
        print(len(list_positive))
        print(len(list_negative)) # launch error if length == 0
        # For each cell type we want to build two matrices to calculate scores:
        gating_positive = sample_data[sample_data.columns.intersection(list_positive)].to_numpy()
        gating_negative = sample_data[sample_data.columns.intersection(list_negative)].to_numpy()
        marker_scores_positive = np.apply_along_axis(score_marker_pos, 0, gating_positive)
        marker_scores_negative = np.apply_along_axis(score_marker_neg, 0, gating_negative)
        marker_scores = np.column_stack((marker_scores_positive,marker_scores_negative))
        normalized_marker_scores = np.apply_along_axis(normalize_scores, 0, marker_scores)
        scores_matrix[:, idx] = np.mean(normalized_marker_scores, 1)
    
def run2(input_path,labels,output_folder):
    levels = list(labels.keys())

    # Read data
    filenames=os.listdir(input_path) 
    # TODO: in settings where multiple samples were in the same slides and can be run together there should be a function to merge them
    for samplefile in filenames:
        sample_data=pd.read_csv(os.path.join(input_path,samplefile))
        for level in levels:
            # Test if the gating needs columns that don't exist
            if set(labels[level].index.values) <= set(sample_data.columns.values):
                # return some error
                return(" ")
            # Filter table to have only the correct channels
            gating_data=sample_data[sample_data.columns[sample_data.columns.isin(labels[level].index.values)]]
            # Z-score standardization
            # Consider if it is necessary at all, it is a super slow process that takes all the cores and all the memory
            gating_data=(gating_data - np.mean(gating_data, axis=0)) / np.std(gating_data, axis=0)
            array_data=gating_data.values
            som_shape = (8, 8)
            som = MiniSom(som_shape[0], som_shape[1], array_data.shape[1], sigma=.5, learning_rate=.5,
              neighborhood_function='gaussian', random_seed=10)

            som.train_batch(array_data, 50000, verbose=True)
            mapped_neurons=som.win_map(array_data)

            winner_coordinates = np.array([som.winner(x) for x in array_data]).T
            # with np.ravel_multi_index we convert the bidimensional
            # coordinates to a monodimensional index
            cluster_index = np.ravel_multi_index(winner_coordinates, som_shape)
            
            #processLevel(level)
        # concat results: data + level1 + level2 + level3 ...
        # return(results)
        # write CSV files in result folder
# EOF
        
    