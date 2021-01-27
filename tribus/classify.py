''' Start point of the command tribus classify '''
import numpy as np
import pandas as pd
from minisom import MiniSom
import os

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
    # TODO: PARALLELIZE HERE

    nodes = somClustering(cells)
    scores = scoreNodes(nodes, rules)
    labeled_data = assignLabels(scores)
    return(labeled_data)

def run(input_path,labels,output_folder):
    input_path='input_data'
    logic_path='gate_logic_1.xlsx'
    output_folder='test_results'


    df = pd.ExcelFile(logic_path)
    labels = pd.read_excel(df, df.sheet_names, index_col=0)

    levels = list(labels.keys())

    # Read data
    filenames=os.listdir(input_path) 
    for samplefile in filenames:
        sample_data=pd.read_csv(os.path.join(input_path,samplefile))
        for level in levels:
            if set(labels[level].index.values) <= set(sample_data.columns.values):
                # continue here
                return(" ")
            # Filter table to have only the correct channels
            gating_data=sample_data[sample_data.columns[sample_data.columns.isin(labels[level].index.values)]]
            gating_data=(gating_data - np.mean(gating_data, axis=0)) / np.std(gating_data, axis=0)
            gating_data=gating_data.values
            som_shape = (8, 8)
            som = MiniSom(som_shape[0], som_shape[1], gating_data.shape[1], sigma=.5, learning_rate=.5,
              neighborhood_function='gaussian', random_seed=10)

            som.train_batch(gating_data, 500, verbose=True)
            som.win_map()
            
            #processLevel(level)
        # concat results: data + level1 + level2 + level3 ...
        # return(results)
        # write CSV files in result folder

        
    