''' Start point of the command tribus classify '''
import numpy as np
import pandas as pd
from minisom import MiniSom
from sklearn_som.som import SOM
#from FlowGrid import *
from pathlib import Path
import os
import sys
from sklearn.cluster import SpectralClustering
import scanpy.external as sce
from sklearn.cluster import AgglomerativeClustering

def clusterCells(grid_size, sample_data, labels, level):
    '''run self-organized map to assign cells to nodes'''
    marker_data = sample_data[labels[level].index.values].to_numpy()
    #TODO: choose clustering variables based on data length and width, number of labels in level and number of levels
    som = SOM(m=grid_size, n=grid_size, dim=marker_data.shape[1])
    som.fit(marker_data)
    predictions = som.predict(marker_data)
    unique, counts = np.unique(predictions, return_counts=True)
    # For each node calculate median expression of each gating marker
    labeled = sample_data[labels[level].index.values].copy()
    labeled['label'] = predictions
    data_to_score = labeled.groupby('label').median()
    return(data_to_score, labeled)

def clusterCellsPhenoGraph(grid_size, sample_data, labels, level):
    '''run self-organized map to assign cells to nodes'''
    marker_data = sample_data[labels[level].index.values].to_numpy()
    # TODO: choose clustering variables based on data length and width, number of labels in level and number of levels
    predicted_labels, graph, Q = sce.tl.phenograph(marker_data, primary_metric = 'correlation', k = grid_size, min_cluster_size=10, nn_method='brute')
    print('modularity score:', Q)
    unique, counts = np.unique(labels, return_counts=True)
    # For each node calculate median expression of each gating marker
    predictions = predicted_labels
    labeled = sample_data[labels[level].index.values].copy()
    labeled['label'] = predictions
    data_to_score = labeled.groupby('label').median()
    return (data_to_score, labeled)


# TODO: function evaluate the weight and importance of each channel in the clustering result

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
    res = [ (np.percentile(x, 99) - i)**2 for i in x]
    return res

def score_marker_neg(x):
    res = [ (i - np.min(x))**2 for i in x]
    return res

def normalize_scores(x):
    res = 1 - ((x - np.min(x)) / (np.max(x) - np.min(x)))
    return res

def scoreNodes(data_to_score, labels, level):
    '''scoring function'''
    level_logic_df = labels[level]
    scores_matrix = np.zeros((data_to_score.shape[0], labels[level].shape[1]))
    for idx, cell_type in enumerate(labels[level].columns.values):
        list_negative = list(level_logic_df.loc[level_logic_df[cell_type] == -1].index)
        list_positive = list(level_logic_df.loc[level_logic_df[cell_type] == 1].index)
        # TODO: launch error if len(list_positive) == 0
        #raise Error
        gating_positive = data_to_score[list_positive].to_numpy()
        gating_negative = data_to_score[list_negative].to_numpy()
        #
        marker_scores_positive = np.apply_along_axis(score_marker_pos, 0, gating_positive)
        marker_scores_negative = np.apply_along_axis(score_marker_neg, 0, gating_negative)
        #
        marker_scores = np.column_stack((marker_scores_positive,marker_scores_negative))
        normalized_marker_scores = np.apply_along_axis(normalize_scores, 0, marker_scores)
        scores_matrix[:, idx] = np.mean(normalized_marker_scores, 1)
    scores_pd = pd.DataFrame(scores_matrix, columns=labels[level].columns.values, index=data_to_score.index)
    return(scores_pd)

def subset(sample_data, current_level, previous_level, previous_labels):
    if previous_labels.empty:
        return sample_data
    labels_tumor = previous_labels.loc[previous_labels[previous_level] == current_level]
    indeces = list(labels_tumor.index)
    new_data = sample_data.loc[indeces, :]
    return new_data

def clustering(grid_size, sample_data, labels, level):
    data_to_score, labeled = clusterCells(grid_size, sample_data, labels, level)
    scores_pd = scoreNodes(data_to_score, labels, level)

    # assign highest scored label
    scores_pd['label'] = scores_pd.idxmax(axis=1)

    #print("scores_pd", scores_pd)
    #print("labeled", labeled)

    # TODO: Write "Other" if highest score is too low
    # back to single cell ordered list to return only labels
    # res=scores_pd.loc[labeled['label']]
    res = scores_pd.loc[labeled['label']].label
    res = pd.DataFrame(res)
    print(res)
    res = res.set_index(labeled.index)
    #res = res.rename(columns={'label': level})
    res = res.rename(columns={'label': "new_level"})
    return res

def traverse(tree, depth, grid_size, sample_data, labels, max_depth, node, previous_level, result_table, previous_labels):
    print(node)
    if depth > max_depth:
        return result_table
    if node in previous_labels.columns:
        result = previous_labels[node]
    else:
        data_subset = subset(sample_data, node, previous_level, result_table)
        result = clustering(grid_size, data_subset, labels, node)

    result_table = result_table.join(result)
    out_edges = tree.out_edges(node)
    for i, j in out_edges:
        traverse(tree, depth+1, grid_size, sample_data, labels, max_depth, j, i, result_table, previous_labels)
    return result_table

def run(samplefilename, input_path,labels,output_folder, level_ids, previous_labels, tree):
    """ Labels one sample file. Iterative function that subsets data based on previous labels until all levels are done.
    Keyword arguments:
      input_path      -- path to a single CSV file
      labels          -- Pandas dataframe
      output_folder   -- May be used for intermediate plots or for probabilities/scores
      levels          -- list of consecutive integers corresponding to tabs in the logic file - For now assume it's 0
    """
    sample_data = pd.read_csv(input_path)
    levels = list(labels.keys())
    result_table = pd.DataFrame()
    print(level_ids)
    for level_id in level_ids:
        level = levels[level_id]
        print(level)
        # Test if the gating needs columns that don't exist. TODO #12 test that only channels with non-zero values
        if set(sample_data.columns.values).issubset(set(labels[level].index.values)):
            print("Gating columns missing in data", file=sys.stderr)
            return(False)
        #if previous_labels is not None:
            # TODO: subset data
        #    print("this feature is not yet implemented")
        #    return(False)
        else:
            # Assume we start with level 0            
            # Cluster
            grid_size= 5
            data_to_score, labeled = clusterCells(grid_size, sample_data, labels, level)
            #print("data_to_score", data_to_score)
            #print("labeled", labeled)
            # Score clusters
            scores_pd = scoreNodes(data_to_score, labels, level)
            # assign highest scored label
            scores_pd['label'] = scores_pd.idxmax(axis=1)
            # Write down scores as CSV files inside level loop?
            scores_folder = os.path.join(output_folder, 'celltype_scores')
            Path(scores_folder).mkdir(parents=True, exist_ok=True)
            scores_pd.to_csv(scores_folder + os.sep + 'scores_' + samplefilename)
            data_to_score.to_csv(scores_folder + os.sep + 'data_to_scores_' + samplefilename)

            # TODO: Write "Other" if highest score is too low
            # back to single cell ordered list to return only labels
            #res=scores_pd.loc[labeled['label']]
            res = scores_pd.loc[labeled['label']].label
            result_table[level] = list(res)
            new_data = subset(sample_data, labels, level, result_table)
            new_table = pd.DataFrame()
            new_res = clustering(grid_size, new_data, labels, level, new_table)
            result_table = result_table.join(new_res)
            return result_table
            # Create label vector AND append to previous_labels
    return result_table
    # return full label table
    
# EOF
        
    