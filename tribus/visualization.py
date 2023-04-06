import pandas as pd
import numpy as np
import seaborn as sns
import scipy.stats as stats
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import matplotlib
from umap import UMAP
import math
import matplotlib.backends.backend_pdf
from matplotlib.patches import Patch

palette = sns.dark_palette("#FF0000", as_cmap=True)
matplotlib.cm.register_cmap("mycolormap", palette)


def correlation_matrix(table, markers, figsize_=(10, 10), cmap_='vlag', title=""):
    correlation_mx = pd.DataFrame()
    for marker1 in markers:
        correlations = []
        for marker2 in markers:
            correlations.append(np.corrcoef(list(table[marker1]), list(table[marker2]))[0, 1])
        correlation_mx[marker1] = correlations
    correlation_mx.index = markers
    sns.clustermap(correlation_mx, figsize=figsize_, cmap=cmap_).fig.suptitle(
        title, fontweight="bold", y=0.99)
    return correlation_mx


def z_score(df):
    return df.apply(stats.zscore)


def get_markers(cell_type_description):
    markers = list(cell_type_description.iloc[:, 0])
    return markers


def get_cell_types(labels):
    return np.unique(labels)


def get_subsets(sample_file, labels):
    cell_types = np.unique(labels)
    sample_file.loc[:, 'labels'] = labels
    subsets = []
    normal_cell_types = []
    for cell_type in cell_types:
        if "undefined" in cell_type or "other" in cell_type:
            continue
        else:
            subsets.append(sample_file.loc[sample_file['labels'] == cell_type])
            normal_cell_types.append(cell_type)
    return subsets, normal_cell_types


def heatmap_for_median_expression(sample_file, labels, description_table,  transform=z_score, title="",
                                  c_palette=sns.color_palette(['lightsteelblue', 'ivory', 'indianred'], 3),
                                  cmap_='vlag', dendrogram_ratio_=0.1):

    df_median = pd.DataFrame()
    df_annotation_table = pd.DataFrame()
    markers = list(description_table.index)
    filtered_sample = sample_file[markers]
    table, cell_types = get_subsets(filtered_sample, labels)

    for i in range(len(cell_types)):
        df_median[cell_types[i]] = table[i].iloc[:,:-1].median()
        new_value = description_table[cell_types[i]]
        palette = c_palette
        lut = dict(zip(np.unique(new_value), palette))
        row_colors = new_value.map(lut)
        df_annotation_table[cell_types[i]] = list(row_colors)


    df_annotation_table = df_annotation_table.set_index(df_median.index)
    df_median = transform(df_median.transpose())
    sns.clustermap(df_median, figsize=(10, 8), cmap=cmap_, col_colors=df_annotation_table,
                   dendrogram_ratio=dendrogram_ratio_, colors_ratio=0.02).fig.suptitle(title, fontweight="bold", y=1.01)
    handles = [Patch(facecolor=lut[name]) for name in lut]
    plt.legend(handles, lut, title='Expected values',
           bbox_to_anchor=(1, 1), bbox_transform=plt.gcf().transFigure, loc='upper right')
    return df_median


def umap_vis(sample_file, labels, markers, transformation, title, init='spectral', random_state=0,
             n_neighbors=10, min_dist=0.1, metric='correlation', palette_cell = 'mycolormap', palette_markers='tab10'):

    sample_file_fileterd = sample_file[markers]
    _, cell_types = get_subsets(sample_file_fileterd, labels)
    features = transformation(sample_file_fileterd)
    table = sample_file_fileterd.loc[:, 'labels'] = labels

    proj_2d = pd.DataFrame(
        data=UMAP(n_components=2, init=init, random_state=random_state, n_neighbors=n_neighbors,
                  min_dist=min_dist, metric=metric).fit_transform(features), columns=["component 1", "component 2"])
    rows = math.ceil(len(markers) / 3)
    fig, ax = plt.subplots(rows, 3, figsize=(25, 30))
    fig.suptitle(title, fontsize=30)

    for i in range(len(markers)):
        if markers[i] == 'labels':
            nr_of_colors = len(cell_types)
            palette = sns.color_palette(palette_markers, nr_of_colors)
            proj_2d[markers[i]] = table[markers[i]]
            sns.scatterplot(data=proj_2d, x="component 1", y="component 2", ax=ax[int(i / 3)][i % 3], alpha=0.8,
                            hue=markers[i], palette=palette)
        else:
            proj_2d[markers[i]] = table[markers[i]]

            sns.scatterplot(data=proj_2d, x="component 1", y="component 2", ax=ax[int(i / 3)][i % 3], alpha=0.8,
                            hue=markers[i], palette=palette_cell)