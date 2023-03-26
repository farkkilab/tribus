''' Start point of the command tribus classify '''
import numpy as np
import pandas as pd
from sklearn_som.som import SOM
import math

## Constants
MAX_PERCENTILE = 99
REQUIRED_CELLS_FOR_CLUSTERING = 0
THRESHOLD_LOW = 0.4
THRESHOLD_CLOSE = 0.01


def cluster_cells(sample_data, labels, level):
    '''run self-organized map to assign cells to nodes'''
    grid_size = int(np.sqrt(np.sqrt(len(sample_data)) * 5))
    marker_data = sample_data[labels[level].index.values].to_numpy()

    som = SOM(m=grid_size, n=grid_size, dim=marker_data.shape[1])
    som.fit(marker_data)
    predictions = som.predict(marker_data)
    unique, counts = np.unique(predictions, return_counts=True)

    # For each node calculate median expression of each gating marker
    labeled = sample_data[labels[level].index.values].copy()
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


def get_cell_type(x, level):
    sorted_ = np.sort(x)
    highest = sorted_[-1]
    second_highest = sorted_[-2]
    if highest < THRESHOLD_LOW:
        return f'other_{level}'
    if highest-second_highest < THRESHOLD_CLOSE:
        return f'undefined_{level}'
    return x.idxmax()


def get_probabilities(x):
    return np.max(x)


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
        scores_matrix[:, idx] = np.mean(normalized_marker_scores, 1) # put the mean of the marker values of a celltype into a matrix (indexed by the celltypes)
    scores_pd = pd.DataFrame(scores_matrix, columns=labels[level].columns.values, index=data_to_score.index)
    return scores_pd


def subset(sample_data, current_level, previous_level, previous_labels):
    if previous_labels.empty:
        return sample_data
    labels_tumor = previous_labels.loc[previous_labels[previous_level] == current_level]
    indeces = list(labels_tumor.index)
    new_data = sample_data.loc[indeces, :]
    return new_data


def clustering(sample_data, labels, level):
    print(level)

    if len(sample_data) < REQUIRED_CELLS_FOR_CLUSTERING:
        print("less than min sample_size")
        # This will score each cell without need for clustering, the constant should be changed after testing for single cell clustering
        data_to_score = sample_data
        scores_pd = score_nodes(data_to_score, labels, level)
        scores_labels = pd.DataFrame()
        scores_labels['cell_label'] = scores_pd.apply(lambda x: get_cell_type(x, level), axis=1)
        scores_labels['probability'] = scores_pd.apply(get_probabilities, axis=1)
        labels_list = scores_labels.cell_label
        prob_list = scores_labels.probability
        labels_df = pd.DataFrame(labels_list)
        labels_df = labels_df.set_index(sample_data.index)
        prob_df = pd.DataFrame(prob_list)
        prob_df = prob_df.set_index(sample_data.index)


    else: # if enough cells, do clustering

        # get a table, rows are the clusters and columns are the cell-types, having the scoring, highest the more probable
        data_to_score, labeled = cluster_cells(sample_data, labels, level)
        scores_pd = score_nodes(data_to_score, labels, level)
        # assign highest scored label
        scores_labels = pd.DataFrame()
        scores_labels['cell_label'] = scores_pd.apply(lambda x: get_cell_type(x, level), axis=1)
        scores_labels['probability'] = scores_pd.apply(get_probabilities, axis=1)
        labels_list = scores_labels.loc[labeled['label']].cell_label # according to the cluster labels, assign the most probable cell-type to each cell
        prob_list = scores_labels.loc[labeled['label']].probability
        labels_df = pd.DataFrame(labels_list)
        labels_df = labels_df.set_index(labeled.index)
        prob_df = pd.DataFrame(prob_list)
        prob_df = prob_df.set_index(labeled.index)


    # TODO: Write "Other" if highest score is too low
    labels_df = labels_df.rename(columns={'cell_label': level})
    prob_df = prob_df.rename(columns={'probability': level})
    return labels_df, prob_df


def traverse(tree, depth, sample_data, labels, max_depth, node, previous_level, result_table, prob_table,
             previous_labels):
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
            result, prob = clustering(data_subset, labels, node)
            print(f'{node}, clustering done')

        if result_table.empty:
            result_table = result
            prob_table = prob
        else:
            result_table = result_table.join(result)
            prob_table = prob_table.join(prob)

        out_edges = tree.out_edges(node)
        for i, j in out_edges:
            result_table, prob_table = traverse(tree, depth + 1, sample_data, labels, max_depth, j, i, result_table,
                                                prob_table, previous_labels)
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


def run(sample_data, labels, depth, previous_labels, tree):
    """
    # create an output folder for intermediate results
    scores_folder = os.path.join(output_folder, 'celltype_scores')
    Path(scores_folder).mkdir(parents=True, exist_ok=True)
    """

    result_table = pd.DataFrame()
    prob_table = pd.DataFrame()
    result_table, prob_table = traverse(tree, 0, sample_data, labels, depth, "Global", pd.DataFrame(), result_table,
                                        prob_table, previous_labels)

    final_cell_type = get_final_cells(result_table)
    final_prob = get_final_prob(prob_table)

    result_table["final_label"] = final_cell_type
    prob_table["final_probability"] = final_prob

    return result_table, prob_table
    # return full label table

# EOF
