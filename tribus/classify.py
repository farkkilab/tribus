''' Start point of the command tribus classify '''
import numpy as np
import pandas as pd
from sklearn_som.som import SOM
import math
import visualization


## Constants
MAX_PERCENTILE = 99


def cluster_cells(sample_data, logic, level, random_state):
    '''run self-organized map to assign cells to nodes
    sample_data: dataframe
    logic: dictionary of dataframes
    level: string
    returns: 2 dataframe, median expression in each node, labeled dataframe (with node ID)
    '''
    grid_size = int(np.sqrt(np.sqrt(len(sample_data)) * 5))
    marker_data = sample_data.to_numpy()


    som = SOM(m=grid_size, n=grid_size, dim=marker_data.shape[1], random_state=random_state)
    som.fit(marker_data)
    predictions = som.predict(marker_data)
    unique, counts = np.unique(predictions, return_counts=True)

    # For each node calculate median expression of each gating marker
    labeled = sample_data[logic[level].index.values].copy()
    labeled['label'] = predictions
    data_to_score = labeled.groupby('label').median()  # for all cells the median marker level of each cluster
    return data_to_score, labeled

"""
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
"""

# TODO: function evaluate the weight and importance of each channel in the clustering result

def processLevel(level):
    '''parallelize for samples if possible'''
    # TODO PARALLELIZE HERE, probably on different branches on the lineage tree
    return ('')


def score_marker_pos(x):
    """
    get the largest value for a marker, subtract from it all the values --> take the squared
    large values will get small values, small values get larger values
    """
    res = [(np.percentile(x, MAX_PERCENTILE) - i) ** 2 for i in x]
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
    if np.max(x) - np.min(x) == 0:
        print(x)

    res = 1 - ((x - np.min(x)) / (np.max(x) - np.min(x)))
    return res


def get_cell_type(x, level, undefined_threshold, other_threshold):
    '''
    assigning cell type based on the score, write "other" if highest score is too low, write "undifined" if the two highest score are too close to eachother
    '''
    sorted_ = np.sort(x)
    highest = sorted_[-1]
    second_highest = sorted_[-2]
    if highest < other_threshold:
        return f'other_{level}'
    if highest-second_highest < undefined_threshold:
        return f'undefined_{level}'
    return x.idxmax()


def get_probabilities(x):
    '''
    assigning the highest probability to each cell
    '''
    return np.max(x)


def score_nodes(data_to_score, logic, level):
    """
    scoring function for the clusters, which cluster belong to which cell-type
    data_to_score: dataframe
    logic: dictionary of dataframes
    level: string
    returns: dataframe
    """
    level_logic_df = logic[level]
    scores_matrix = np.zeros((data_to_score.shape[0], logic[level].shape[1]))
    for idx, cell_type in enumerate(logic[level].columns.values):
        list_negative = list(
            level_logic_df.loc[level_logic_df[cell_type] == -1].index)  # get markers with negative scores
        list_positive = list(
            level_logic_df.loc[level_logic_df[cell_type] == 1].index)  # get markers with positive scores

        if list_positive == 0:
            continue

        gating_positive = data_to_score[list_positive].to_numpy()  # rows: clusters, columns: positive markers
        marker_scores_positive = np.apply_along_axis(score_marker_pos, 0, gating_positive)

        if len(list_negative) != 0:
            gating_negative = data_to_score[list_negative].to_numpy()
            marker_scores_negative = np.apply_along_axis(score_marker_neg, 0, gating_negative)

            marker_scores = np.column_stack((marker_scores_positive, marker_scores_negative))
        else:
            marker_scores = marker_scores_positive

        normalized_marker_scores = np.apply_along_axis(normalize_scores, 0, marker_scores)
        scores_matrix[:, idx] = np.mean(normalized_marker_scores, 1) # put the mean of the marker values of a celltype into a matrix (indexed by the celltypes)
    scores_pd = pd.DataFrame(scores_matrix, columns=logic[level].columns.values, index=data_to_score.index)
    return scores_pd


def subset(sample_data, current_level, previous_level, previous_labels, logic):
    '''
    do the busetting of the sample data, based on the previous results
    sample_data: dataframe
    current_level: string
    previous_level: string
    previous_labels: dataframe
    returns: subsetted dataframe
    '''
    marker_data = sample_data[logic[current_level].index.values]
    if previous_labels.empty:
        return marker_data
    labels_tumor = previous_labels.loc[previous_labels[previous_level] == current_level]
    indeces = list(labels_tumor.index)
    new_data = marker_data.loc[indeces, :]
    return new_data


def clustering(sample_data, logic, level, clustering_threshold, undefined_threshold, other_threshold, random_state):
    '''
    assignig the labels to each cell, either sell by cell or first doing the clustering and then node by node
    sample_data: dataframe
    logic: dataframe
    level: string
    returns: 2 dataframe with labels and the probabilities
    '''

    if len(sample_data) < clustering_threshold:
        print("less than min sample_size")
        # This will score each cell without need for clustering, the constant should be changed after testing for single cell clustering
        data_to_score = sample_data
        scores_pd = score_nodes(data_to_score, logic, level)
        scores_labels = pd.DataFrame()
        scores_labels['cell_label'] = scores_pd.apply(lambda x: get_cell_type(x, level, undefined_threshold, other_threshold), axis=1)
        scores_labels['probability'] = scores_pd.apply(get_probabilities, axis=1)
        labels_list = scores_labels.cell_label
        prob_list = scores_labels.probability
        labels_df = pd.DataFrame(labels_list)
        labels_df = labels_df.set_index(sample_data.index)
        prob_df = pd.DataFrame(prob_list)
        prob_df = prob_df.set_index(sample_data.index)


    else: # if enough cells, do clustering
        # get a table, rows are the clusters and columns are the cell-types, having the scoring, highest the more probable
        data_to_score, labeled = cluster_cells(sample_data, logic, level, random_state)
        scores_pd = score_nodes(data_to_score, logic, level)
        # assign highest scored label
        scores_labels = pd.DataFrame()
        scores_labels['cell_label'] = scores_pd.apply(lambda x: get_cell_type(x, level, undefined_threshold, other_threshold), axis=1)
        scores_labels['probability'] = scores_pd.apply(get_probabilities, axis=1)
        labels_list = scores_labels.loc[labeled['label']].cell_label # according to the cluster labels, assign the most probable cell-type to each cell
        prob_list = scores_labels.loc[labeled['label']].probability
        labels_df = pd.DataFrame(labels_list)
        labels_df = labels_df.set_index(labeled.index)
        prob_df = pd.DataFrame(prob_list)
        prob_df = prob_df.set_index(labeled.index)


    labels_df = labels_df.rename(columns={'cell_label': level})
    prob_df = prob_df.rename(columns={'probability': level})
    return labels_df, prob_df


def traverse(tree, sample_data, logic, max_depth, current_depth, node, previous_level, result_table, prob_table,
             previous_labels, output=None, normalization=None, sample_name=None, clustering_threshold=15_000, undefined_threshold=0.01,
             other_threshold=0.4, random_state=None):
    '''
    travering the lineage tree and run the analysis on each level (node) and do visualization if required
    tree: networkx digraph
    depth: integer
    sample_data: dataframe
    labels: dataframe
    logic: dictionary of dataframes
    max_depth: integer
    node: string (level)
    previous_level: string
    result_table: dataframe
    result_table: dataframe (to store the results)
    prob_table: dataframe (to store the probability values for ech cell)
    previous_labels: dataframe (if we can use the results from a previous run)
    output: string (path to save the figures)
    returns: 2 dataframe with results and probabilities
    '''
    if current_depth < max_depth:
        # check whether there is previously available data, so not necessary to rerun some parts of tribus
        if node in previous_labels.columns:
            print(f'{node} in previous lables')
            result = previous_labels[node]
            result = pd.DataFrame(result, columns=[node])
        else:
            data_subset = subset(sample_data, node, previous_level, result_table, logic)
            print(f'{node}, subsetting done')
            if normalization is not None:
                data_subset = normalization(data_subset)

            # only using the markers which are containing different values than zeros
            filtered_markers = list(logic[node].loc[(logic[node] != 0).any(axis=1)].index)
            logic[node] = logic[node].loc[filtered_markers]
            result, prob = clustering(data_subset, logic, node, clustering_threshold, undefined_threshold, other_threshold, random_state)

        if result_table.empty:
            result_table = result
            prob_table = prob
        else:
            result_table = result_table.join(result)
            prob_table = prob_table.join(prob)
        if output is not None:
            markers = []
            for key in logic:
                markers_ = list(logic[key].index)
                markers = markers + markers_
            markers = list(np.unique(markers))
            sample_data[markers]

            visualization.correlation_matrix(data_subset, markers=list(logic[node].index), level=node, save=True,
                                             fname=f'{output}/{sample_name}_correlation_{node}')

            visualization.heatmap_for_median_expression(data_subset, result_table, logic, level=node, save=True,
                                                        fname=f'{output}/{sample_name}_heatmap_{node}')

            visualization.umap_vis(data_subset, result_table, markers=markers, save=True
                                   , fname=f'{output}/{sample_name}_umap_{node}', level=node)

            visualization.marker_expression_by_cell_type(data_subset, result_table, markers=list(logic[node].index),
                                                         level=node, save=True, fname=f'{output}/{sample_name}_marker_expression_{node}.png')

            visualization.cell_type_distribution(result_table, level=node, save=True, fname=f'{output}/{sample_name}_barplot_{node}.png')
            print("Figures done")

        out_edges = tree.out_edges(node)
        for i, j in out_edges:
            result_table, prob_table = traverse(tree, sample_data, logic, max_depth, current_depth + 1, j, i, result_table,
                                                prob_table, previous_labels, output=output, normalization=normalization,
                                                sample_name=sample_name, clustering_threshold=clustering_threshold,
                                                undefined_threshold=undefined_threshold, other_threshold=other_threshold,
                                                random_state=random_state)
    return result_table, prob_table


def get_final_prob(table):
    new_column = []
    for index, row in table.iterrows():
        lst = list(row)
        for i in range(len(lst) - 1, -1, -1):
            if not math.isnan(lst[i]):
                new_column.append(lst[i])
                break
    return new_column


def get_final_cells(table):
    new_column = []
    for index, row in table.iterrows():
        lst = list(row)
        for i in range(len(lst) - 1, -1, -1):
            if lst[i] == lst[i]:
                new_column.append(lst[i])
                break
    return new_column


def run(sample_data, logic, depth, previous_labels, tree, output=None, normalization=None, sample_name=None,
        clustering_threshold=15_000, undefined_threshold=0.01, other_threshold=0.4, random_state=None):
    """
    tribus main function, running the actual analysis by traversing the lineage tree
    sample_data: dataframe (one sample)
    labels: dictionary (logic)
    depth: integer
    previous_labels: dataframe
    tree: networkx digraph
    output: string (data path)

    returns: 2 dataframe, labels and probabilities
    """

    result_table = pd.DataFrame()
    prob_table = pd.DataFrame()

    if output is not None:
        markers = []
        for key in logic:
            markers_ = list(logic[key].index)
            markers = markers + markers_
        markers = np.unique(markers)
        sample_data[markers]
        visualization.marker_expression(sample_data[markers], save=True, fname=f'{output}/{sample_name}_markerexpression.png')

    result_table, prob_table = traverse(tree, sample_data, logic, depth, 0, "Global", pd.DataFrame(), result_table,
                                        prob_table, previous_labels, output, normalization=normalization, sample_name=sample_name,
                                        clustering_threshold=clustering_threshold, undefined_threshold=undefined_threshold,
                                        other_threshold=other_threshold, random_state=random_state)

    final_cell_type = get_final_cells(result_table)
    final_prob = get_final_prob(prob_table)

    result_table["final_label"] = final_cell_type
    prob_table["final_probability"] = final_prob

    return result_table, prob_table
    # return full label table

# EOF
