import sys
import pandas as pd
import numpy as np
import seaborn as sns
import scipy.stats as stats
import matplotlib.pyplot as plt
import matplotlib
# from umap import UMAP
import umap.umap_ as umap
import math
import matplotlib.backends.backend_pdf
from matplotlib.patches import Patch
import colorcet as cc
from sklearn import preprocessing

palette = sns.dark_palette("#FF0000", as_cmap=True)
matplotlib.cm.register_cmap("mycolormap", palette)


def correlation_matrix(table, markers, save=False, fname=None, dpi="figure", figsize=(10, 10), cmap='vlag', title=""):

    new_table = table.copy()
    correlation_mx = pd.DataFrame()
    for marker1 in markers:
        correlations = []
        for marker2 in markers:
            correlations.append(np.corrcoef(list(new_table[marker1]), list(new_table[marker2]))[0, 1])
        correlation_mx[marker1] = correlations
    correlation_mx.index = markers
    sns.clustermap(correlation_mx, figsize=figsize, cmap=cmap).fig.suptitle(
        title, fontweight="bold", y=0.99)

    if save:
        plt.savefig(fname, dpi=dpi)
        plt.clf()
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
    tables, cell_types = get_subsets(filtered_sample, filtered_labels)

    for i in range(len(cell_types)):
        df_median[cell_types[i]] = tables[i].iloc[:, :-1].median()
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
        plt.savefig(fname, dpi=dpi)
        plt.clf()
    else:
        plt.show()
    return df_median


def umap_vis(sample_file, labels, markers, supervised=False, save=False, fname=None, level="Global", title=None,
             init='spectral',
             random_state=0, n_neighbors=5, min_dist=0.1, metric='correlation', palette_markers='mycolormap',
             palette_cell='tab10', point_size=1,  dpi='figure'):
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


    label_encoder = preprocessing.LabelEncoder()
    y = label_encoder.fit_transform(filtered_labels)

    if supervised:
        proj_2d = pd.DataFrame(
            data=umap.UMAP(n_components=2, init=init, random_state=random_state, n_neighbors=n_neighbors,
                      min_dist=min_dist, metric=metric).fit_transform(sample_file_filtered, y = y),
            columns=["component 1", "component 2"])
    else:
        proj_2d = pd.DataFrame(
            data=umap.UMAP(n_components=2, init=init, random_state=random_state, n_neighbors=n_neighbors,
                      min_dist=min_dist, metric=metric).fit_transform(sample_file_filtered),
            columns=["component 1", "component 2"])

    rows = math.ceil(len(markers) / 3)
    fig, ax = plt.subplots(rows, 3, figsize=(25, 30))
    fig.suptitle(title, fontsize=30)

    for i in range(len(markers)):
        #print(markers[i])
        if markers[i] == 'labels':
            nr_of_colors = len(cell_types)
            palette = sns.color_palette(cc.glasbey, n_colors=nr_of_colors)
            proj_2d[markers[i]] = table[markers[i]]
            sns.scatterplot(data=proj_2d, x="component 1", y="component 2", ax=ax[int(i / 3)][i % 3], alpha=0.8,
                            hue=markers[i], palette=palette, s=point_size)
        else:
            proj_2d[markers[i]] = table[markers[i]]
            sns.scatterplot(data=proj_2d, x="component 1", y="component 2", ax=ax[int(i / 3)][i % 3], alpha=0.8,
                            hue=markers[i], palette=palette_markers, s=point_size)
    if save:
        plt.savefig(fname, dpi=dpi)
        plt.clf()
    else:
        plt.show()


def marker_expression(sample_data, markers=None, save=False, fname=None, dpi='figure', log=False):
    if markers is None:
        markers = sample_data.columns.values

    fig, axs = plt.subplots(math.ceil(len(markers) / 6), 6, squeeze=False, figsize=(30, 20))
    fig.suptitle("Marker expression level", fontsize=30)
    if log:
        for i in range(len(markers)):
            ax = axs[i//6, i%6]
            plt.sca(ax)
            hist, edges = np.histogram(sample_data[markers[i]], bins=50)
            plt.stairs(np.log(hist)+ sys.float_info.epsilon, edges, label="{}".format(markers[i]))
            plt.title(f"{markers[i]}")
            plt.grid()
            plt.tight_layout()
    else:
        for i in range(len(markers)):
            ax = axs[i//6, i%6]
            plt.sca(ax)
            hist, edges = np.histogram(sample_data[markers[i]], bins=50)
            plt.stairs(hist, edges, label="{}".format(markers[i]))
            plt.title(f"{markers[i]}")
            plt.grid()
            plt.tight_layout()
    if save:
        plt.savefig(fname, dpi=dpi)
        plt.clf()
    else:
        plt.show()


def marker_expression_by_cell_type(sample_data, labels, cell_types=None, markers=None, level="Global", save=False, fname=None, dpi='figure', log=False):
    if markers is None:
        markers = sample_data.columns.values

    sample_data_labeled = sample_data.copy()
    sample_data_labeled["label"] = labels[level]
    if cell_types is None:
        cell_types = np.unique(sample_data_labeled["label"])

    fig, axs = plt.subplots(math.ceil(len(markers) / 6), 6, squeeze=False, figsize=(30, 20))
    fig.suptitle("Marker expression level per cell type", fontsize=30)

    if log:
        for i in range(len(markers)):
            ax = axs[i//6, i%6]
            plt.sca(ax)
            for uc in cell_types:
                subset = sample_data_labeled.loc[sample_data_labeled["label"]==uc]
                hist, edges = np.histogram(subset[markers[i]], bins=50)
                plt.stairs(np.log(hist)+sys.float_info.epsilon, edges, label="{}".format(uc))
                plt.legend(loc='upper right')
            plt.title(f"{markers[i]}")
            plt.grid()
            plt.tight_layout()
    else:
        for i in range(len(markers)):
            ax = axs[i//6, i%6]
            plt.sca(ax)
            for uc in cell_types:
                subset = sample_data_labeled.loc[sample_data_labeled["label"]==uc]
                hist, edges = np.histogram(subset[markers[i]], bins=50)
                plt.stairs(hist, edges, label="{}".format(uc))
                plt.legend(loc='upper right')
            plt.title(f"{markers[i]}")
            plt.grid()
            plt.tight_layout()
    if save:
        fig.savefig(fname)
        plt.clf()
    else:
        plt.show()


def cell_type_distribution(labels, level="Global", save=False, fname=None, dpi="Figure"):
    cell_types, counts = np.unique(list(labels[level]), return_counts=True)
    plt.bar(cell_types, counts)
    if save:
        plt.savefig(fname)
        plt.clf()
    else:
        plt.show()


def log_zscore_normalization(df):
    df_ = df.copy()
    log_data = np.log(df_ + 1)
    z_score_data = log_data.apply(stats.zscore)
    return(z_score_data)