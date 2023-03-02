''' Start point of the command tribus classify '''
import numpy as np
import pandas as pd
from minisom import MiniSom
from sklearn_som.som import SOM
# from FlowGrid import *
from pathlib import Path
import os
import sys
from sklearn.cluster import SpectralClustering
import scanpy.external as sce
from sklearn.cluster import AgglomerativeClustering


def cluster_cells(sample_data, labels, level):
    '''run self-organized map to assign cells to nodes'''
    grid_size = int(np.sqrt(np.sqrt(len(sample_data)) * 5))
    marker_data = sample_data[labels[level].index.values].to_numpy()

    # TODO: choose clustering variables based on data length and width, number of labels in level and number of levels
    som = SOM(m=grid_size, n=grid_size, dim=marker_data.shape[1])
    som.fit(marker_data)
    predictions = som.predict(marker_data)
    unique, counts = np.unique(predictions, return_counts=True)

    # For each node calculate median expression of each gating marker
    labeled = sample_data[labels[level].index.values].copy()
    labeled['label'] = predictions
    data_to_score = labeled.groupby('label').median()  # for all cells the median marker level of each cluster
    return data_to_score, labeled


def clusterCellsPhenoGraph(grid_size, sample_data, labels, level):
    '''run self-organized map to assign cells to nodes'''
    marker_data = sample_data[labels[level].index.values].to_numpy()
    # TODO: choose clustering variables based on data length and width, number of labels in level and number of levels
    predicted_labels, graph, Q = sce.tl.phenograph(marker_data, primary_metric='correlation', k=grid_size,
                                                   min_cluster_size=10, nn_method='brute')
    print('modularity score:', Q)
    unique, counts = np.unique(labels, return_counts=True)
    # For each node calculate median expression of each gating marker
    predictions = predicted_labels
    labeled = sample_data[labels[level].index.values].copy()
    labeled['label'] = predictions
    data_to_score = labeled.groupby('label').median()
    return (data_to_score, labeled)


# TODO: function evaluate the weight and importance of each channel in the clustering result

def processLevel(level):
    '''parallelize for samples if possible'''
    # TODO PARALLELIZE HERE
    return ('')


def score_marker_pos(x):
    """
    get the largest value for a marker, subtract from it all the values --> take the squared
    large values will get small values, small values get larger values
    """
    res = [(np.percentile(x, 99) - i) ** 2 for i in x]
    return res


def score_marker_neg(x):
    """
    substrach the minimum from each value --> take the squared
    large values remain large, small values became smaller
    """

    res = [(i - np.min(x)) ** 2 for i in x]
    return res


def normalize_scores(x):
    """
    normalize the values between 0-1
    change the direction of scoring, smaller ones becomes the larger ones and vica versa (inverting)
    """
    res = 1 - ((x - np.min(x)) / (np.max(x) - np.min(x)))
    return res


def score_nodes(data_to_score, labels, level):
    """
    scoring function for the clusters, which cluster belong to which cell-type
    """
    level_logic_df = labels[level]
    scores_matrix = np.zeros((data_to_score.shape[0], labels[level].shape[1]))
    for idx, cell_type in enumerate(labels[level].columns.values):
        list_negative = list(
            level_logic_df.loc[level_logic_df[cell_type] == -1].index)  # get markers with negative scores
        list_positive = list(
            level_logic_df.loc[level_logic_df[cell_type] == 1].index)  # get markers with positive scores

        gating_positive = data_to_score[list_positive].to_numpy()  # rows: clusters, columns: positive markers
        marker_scores_positive = np.apply_along_axis(score_marker_pos, 0, gating_positive)

        if len(list_negative) != 0:
            gating_negative = data_to_score[list_negative].to_numpy()
            marker_scores_negative = np.apply_along_axis(score_marker_neg, 0, gating_negative)

            marker_scores = np.column_stack((marker_scores_positive, marker_scores_negative))
        else:
            marker_scores = marker_scores_positive

        normalized_marker_scores = np.apply_along_axis(normalize_scores, 0, marker_scores)
        scores_matrix[:, idx] = np.mean(normalized_marker_scores, 1)  # put the mean of the marker values of a celltype into a matrix (indexed by the celltypes)
    scores_pd = pd.DataFrame(scores_matrix, columns=labels[level].columns.values, index=data_to_score.index)
    return scores_pd


def subset(sample_data, current_level, previous_level, previous_labels):
    if previous_labels.empty:
        return sample_data
    labels_tumor = previous_labels.loc[previous_labels[previous_level] == current_level]
    indeces = list(labels_tumor.index)
    new_data = sample_data.loc[indeces, :]
    return new_data


def clustering(sample_data, labels, level, scores_folder, samplefilename):
    data_to_score, labeled = cluster_cells(sample_data, labels, level)
    print(level)

    #get a table, rows are the clusters and columns are the cell-types, having the scoring, highest the more probable
    scores_pd = score_nodes(data_to_score, labels, level)
    scores_pd['label'] = scores_pd.idxmax(axis=1)
    scores_pd.to_csv(scores_folder + os.sep + 'scores_' + level + '_' + samplefilename)
    data_to_score.to_csv(scores_folder + os.sep + 'data_to_scores_' + level + '_' + samplefilename)

    # TODO: Write "Other" if highest score is too low, probably threshold for 0.5

    res = scores_pd.loc[labeled['label']].label #according to the cluster labels, assign the most probable cell-type to each cell
    res = pd.DataFrame(res)
    res = res.set_index(labeled.index)
    res = res.rename(columns={'label': level})
    return res


def traverse(tree, depth, sample_data, labels, max_depth, node, previous_level, result_table, previous_labels,
             scores_folder, filename):
    if depth < max_depth:
        # check whether there is previously available data, so not necessary to rerun some parts of tribus
        if node in previous_labels.columns:
            print(f'{node} in previous lables')
            result = previous_labels[node]
            result = pd.DataFrame(result, columns=[node])
        else:
            data_subset = subset(sample_data, node, previous_level, result_table)
            print(f'{node}, subsetting done')

            # only using the markers which are containing different values than zeros
            filtered_markers = list(labels[node].loc[(labels[node] != 0).any(axis=1)].index)
            labels[node] = labels[node].loc[filtered_markers]

            result = clustering(data_subset, labels, node, scores_folder, filename)
            print(f'{node}, clustering done')

        if result_table.empty:
            result_table = result
        else:
            result_table = result_table.join(result)

        out_edges = tree.out_edges(node)
        for i, j in out_edges:
            result_table = traverse(tree, depth + 1, sample_data, labels, max_depth, j, i, result_table,
                                    previous_labels, scores_folder, filename)
    return result_table


def run(sample_data, file_ename, labels, output_folder, level_ids, previous_labels, tree):
    """ Labels one sample file. Iterative function that subsets data based on previous labels until all levels are done.
    Keyword arguments:
      input_path      -- Pandas dataframe
      labels          -- Pandas dataframe
      output_folder   -- May be used for intermediate plots or for probabilities/scores
    """
    # create an output folder for intermediate results
    scores_folder = os.path.join(output_folder, 'celltype_scores')
    Path(scores_folder).mkdir(parents=True, exist_ok=True)

    result_table = pd.DataFrame()
    result_table = traverse(tree, 0, sample_data, labels, level_ids, "Global", pd.DataFrame(), result_table,
                            previous_labels, scores_folder, file_ename)
    return result_table
    # return full label table

# EOF
