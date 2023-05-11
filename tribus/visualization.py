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
import colorcet as cc
from sklearn import preprocessing

palette = sns.dark_palette("#FF0000", as_cmap=True)
matplotlib.cm.register_cmap("mycolormap", palette)


def correlation_matrix(table, markers, labels=None, level="Global", save=False, fname=None, dpi="figure",
                       figsize_=(10, 10), cmap_='vlag', title=""):
    if labels is not None:
        new_table = table[labels[level].notnull()]
    else:
        new_table = table.copy()

    correlation_mx = pd.DataFrame()
    for marker1 in markers:
        correlations = []
        for marker2 in markers:
            correlations.append(np.corrcoef(list(new_table[marker1]), list(new_table[marker2]))[0, 1])
        correlation_mx[marker1] = correlations
    correlation_mx.index = markers
    sns.clustermap(correlation_mx, figsize=figsize_, cmap=cmap_).fig.suptitle(
        title, fontweight="bold", y=0.99)

    if save:
        plt.save(fname, dpi=dpi)
    else:
        plt.show()

    return correlation_mx


def get_subsets(sample_file, labels):
    cell_types = np.unique(labels)
    new_file = sample_file.copy()
    new_file.loc[:, 'labels'] = labels
    subsets = []
    normal_cell_types = []
    for cell_type in cell_types:
        if "undefined" in cell_type or "other" in cell_type:
            continue
        else:
            subsets.append(new_file.loc[new_file['labels'] == cell_type])
            normal_cell_types.append(cell_type)
    return subsets, normal_cell_types


def z_score(df):
    return df.apply(stats.zscore)


def get_markers(cell_type_description):
    markers = list(cell_type_description.iloc[:, 0])
    return markers

def log_transform(df):
    log = preprocessing.FunctionTransformer(np.log1p).fit_transform(df.transpose())
    res = pd.DataFrame(np.transpose(log), columns=df.columns).set_index(df.index)
    return res

def get_cell_types(labels):
    return np.unique(labels)


def heatmap_for_median_expression(sample_file, labels, logic, level="Global", save=False, fname=None,
                                  dpi='figure', transform=z_score, title="",
                                  c_palette=sns.color_palette(['lightsteelblue', 'ivory', 'indianred'], 3),
                                  cmap_='vlag', dendrogram_ratio_=0.1):

    df_median = pd.DataFrame()
    df_annotation_table = pd.DataFrame()
    markers = list(logic[level].index)
    filtered_sample = sample_file[markers]
    filtered_sample = filtered_sample[labels[level].notnull()]
    filtered_labels = labels[level][labels[level].notnull()]
    description_table = logic[level]
    values = [-1, 0, 1]
    table, cell_types = get_subsets(filtered_sample, filtered_labels)

    for i in range(len(cell_types)):
        df_median[cell_types[i]] = table[i].iloc[:,:-1].median()
        new_value = description_table[cell_types[i]]
        palette_ = c_palette
        lut = dict(zip(values, palette_))
        row_colors = new_value.map(lut)
        df_annotation_table[cell_types[i]] = list(row_colors)


    df_annotation_table = df_annotation_table.set_index(df_median.index)
    df_median = transform(df_median.transpose())
    sns.clustermap(df_median, figsize=(10, 8), cmap=cmap_, col_colors=df_annotation_table,
                   dendrogram_ratio=dendrogram_ratio_, colors_ratio=0.02).fig.suptitle(title, fontweight="bold", y=1.01)
    handles = [Patch(facecolor=lut[name]) for name in lut]
    plt.legend(handles, lut, title='Expected values', bbox_to_anchor=(1, 1), bbox_transform=plt.gcf().transFigure,
               loc='upper right')

    if save:
        plt.save(fname, dpi = dpi)
    else:
        plt.show()
    return df_median


def umap_vis(sample_file, labels, markers, transform = log_transform, save = False, fname = None,  level = "Global", title = None, init='spectral',
             random_state=0, n_neighbors=10, min_dist=0.1, metric='correlation', palette_markers='mycolormap',
             palette_cell='tab10', dpi='figure'):

    if type(markers) is dict:
        markers = list(markers[level].index)

    if title is None:
        title = str(level)

    filtered_labels = labels[level][labels[level].notnull()]
    sample_file_filtered = sample_file[labels[level].notnull()]

    sample_file_filtered = sample_file_filtered[markers]
    cell_types = np.unique(filtered_labels)
    table = sample_file_filtered.copy()
    table.loc[:, 'labels'] = filtered_labels
    markers.append('labels')
    sample_file_filtered = transform(sample_file_filtered)

    proj_2d = pd.DataFrame(
        data=UMAP(n_components=2, init=init, random_state=random_state, n_neighbors=n_neighbors,
                  min_dist=min_dist, metric=metric).fit_transform(sample_file_filtered), columns=["component 1", "component 2"])
    rows = math.ceil(len(markers) / 3)
    fig, ax = plt.subplots(rows, 3, figsize=(25, 30))
    fig.suptitle(title, fontsize=30)

    for i in range(len(markers)):
        print(markers[i])
        if markers[i] == 'labels':
            nr_of_colors = len(cell_types)
            palette = sns.color_palette(cc.glasbey, n_colors=nr_of_colors)
            proj_2d[markers[i]] = table[markers[i]]
            sns.scatterplot(data=proj_2d, x="component 1", y="component 2", ax=ax[int(i / 3)][i % 3], alpha=0.8,
                            hue=markers[i], palette=palette)
        else:
            proj_2d[markers[i]] = table[markers[i]]
            sns.scatterplot(data=proj_2d, x="component 1", y="component 2", ax=ax[int(i / 3)][i % 3], alpha=0.8,
                            hue=markers[i], palette=palette_markers)
    if save:
        plt.savefig(fname, dpi=dpi)
    else:
        plt.show()

