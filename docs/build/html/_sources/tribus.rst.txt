Cell type annotation
====================

TRIBUS can perform cell-type annotation on multiple samples via reading them from the file and
save the results automatically along with plots of the results. It can also take Pandas dataframes as input and
return the results directly.

run_tribus_from_file
---------------------

Run the cell type annotation on all the samples, which are in the input folder and automatically save
the results into a time-stamped output folder.

.. py:function:: run_tribus_from_file (input_path, output, logic_path, depth=1, save_figures=False, normalization=None)

   :param input_path: Path for the input folder (all files in the folder has to be sample for the analysis)
   :type input_path: str
   :param output: Path for the output folder
   :type input_path: str
   :param logic_path: Path for the cell type description table (xlsx)
   :type logic_path: str
   :param depth: it determines how many levels (of the lineage tree) do we want to perform the analysis
   :type depth: int
   :param save_figures: if True it save automatic diagnostic plots about the input data and the results
   :type save_figures: bool
   :param normalization: A function for data normalization. The function should get a dataframe as an input and it should
    return the normalized data in the same format as the input (same index and column names).
    Tribus will perform the normalization on each level, so the data will be normalized also pre cell type on the
    higher levels. Two type of normalization is available from tribus visualization modul (log normalization and z score
    normalization)
   :type normalization: function

.. code-block:: python

    from tribus import run_tribus_from_file

    run_tribus_from_file(input_path, output_path, logic_path)


An example for the format of the result table:

.. csv-table:: Result labels
   :file: /Users/farateod/Documents/GitHub/tribus/docs/source/mock_labels.csv
   :widths: auto
   :stub-columns: 1
   :header-rows: 1

run_tribus
---------------------

Run the cell type annotation on one sample, and return the results as pandas dataframes. This function makes it possible to
use TRIBUS from Jupyter Notebooks and to make fast evaluations and tune the cell-type-description table.

.. py:function:: run_tribus (input_df, logic, depth=1, normalization=None)

   :param input_df: sample data, where columns are the markers and rows ar the cells, the first column has ro be the Cell ID
   :type input_df: pandas dataframe
   :param logic: dictionary of dataframes, where key are the sheets names, of the excel file, which represents the levels, while the values are the cell type description table
   :type logic: dict
   :param depth: it determines how many levels (of the lineage tree) do we want to perform the analysis
   :type depth: int
   :param normalization: A function for data normalization. The function should get a dataframe as an input and it should
    return the normalized data in the same format as the input (same index and column names).
    Tribus will perform the normalization on each level, so the data will be normalized also pre cell type on the
    higher levels. Two type of normalization is available from tribus visualization modul (log normalization and z score
    normalization)
   :type normalization: function
   :return: df of the cell labels and another df with the probability score of the labels
   :rtype: (pandas dataframe, pandas dataframe)

.. code-block:: python

    from tribus import run_tribus
    import pandas as pd

    sample_data = pd.read_csv(path_sample)
    df_logic = pd.ExcelFile(path_logic)
    logic = pd.read_excel(df_logic, df.sheet_names, index_col=0)
    labels, probabilities = run_tribus(sample_data, logic)
    print(labels.head())

.. csv-table::
   :file: /Users/farateod/Documents/GitHub/tribus/docs/source/mock_labels.csv
   :widths: auto
   :stub-columns: 1
   :header-rows: 1

.. code-block:: python

    print(probabilities.head())


Visualization
=============

The TRIBUS model offer various visiualizations to better understand the inout data and to evaluate the results.

correlation_matrix
---------------------

Plots the correlation between the markers. Helps to evaluate the input data. If the data has high quality and normalized,
the markers, which describes a cell-type should be correlated to each-other.

.. py:function:: correlation_matrix(sample_data, markers, save=False, fname=None, dpi="figure", figsize=(10, 10), cmap='vlag', title="")

   :param sample_data: sample data, where columns are the markers and rows ar the cells, the first column has ro be the Cell ID
   :type sample_data: pandas dataframe
   :param markers: list of the markers, which we would like to plot the correlation inbetween
   :type markers: list[str]
   :param save: if True it save the plot with the given fname
   :type save: bool
   :param fname: the file name, if save=True
   :type fname: str

.. code-block:: python

    from tribus import correlation_matrix
    import pandas as pd

    df = pd.read_csv(path)
    markers = df.columns()
    correlation_matrix(df, markers)

.. image:: corr_matrix_new.png
   :width: 600

marker_expression
------------------

It plots the histogram of the each marker expression in the cells. The shape of the histogram can help to decide whether the data
is well-normalized,  which markers have no variation (it might to worth to exclude them from the analysis), or if outlier filering is needed.

.. py:function:: marker_expression(sample_data, markers=None, save=False, fname=None, dpi='figure', log=False)

   :param sample_data: sample data, where columns are the markers and rows ar the cells, the first column has ro be the Cell ID
   :type sample_data: pandas dataframe
   :param markers: list of the markers, which we would like to plot the correlation inbetween
   :type markers: list[str]
   :param save: if True it save the plot with the given fname
   :type save: bool
   :param fname: the file name, if save=True
   :type fname: str
   :param log: use logarithmic scale on y axis, if save=True
   :type log: bool

.. code-block:: python

    from tribus import marker_expression
    import pandas as pd

    df = pd.read_csv(path)
    markers = df.columns()
    marker_expression(df, markers)

.. image:: marker_expression.png
   :width: 600


marker_expression_by_cell_type
-------------------------------

It plots the histogram of the each marker expression in the cells separately for each cell type identified by TRIBUS. This plot can
help to evaluate the results, and point out it changes needed in the cell-type description table.

.. py:function:: marker_expression_by_cell_type(sample_data, labels, cell_types=None, markers=None, level="Global", save=False, fname=None, dpi='figure', log=False)

   :param sample_data: sample data, where columns are the markers and rows ar the cells, the first column has ro be the Cell ID
   :type sample_data: pandas dataframe
   :param labels: the labels generated by TRIBUS
   :type labels: pandas dataframe
   :param cell_types: the list of cell_types what we want to visualize, if None: it will visualize all the cell types appearing in labels
   :type cell_types: list or None
   :param markers: list of the markers, which we would like to plot the correlation inbetween, if None, it will visualize all the columns in sample data
   :type markers: list[str]
   :param level: which level of the labels do we want to visilaize, default will visualize the highest level
   :type level: str
   :param save: if True it save the plot with the given fname
   :type save: bool
   :param fname: the file name, if save=True
   :type fname: str
   :param log: use logarithmic scale on y axis, if save=True
   :type log: bool

.. code-block:: python

    from tribus import marker_expression_by_cell_type
    import pandas as pd

    sample_data = pd.read_csv(path)
    df_logic = pd.ExcelFile(path_logic)
    logic = pd.read_excel(df_logic, df.sheet_names, index_col=0)
    labels, _ = run_tribus(sample_data, logic)
    marker_expression_by_cell_type(df, labels)

.. image:: merker_expressions_cell_type.png
   :width: 600

heatmap_for_median_expression
------------------------------

This is probably the most important plot in the module, it is a big help in the evaluation of the results.
It shows the median expression of each marker among the cell type, while it also display the cell-type description table,
so it is easy to compare the results with the expected values. The median expression values are z-score normalized by markers
to make the plot more descriptive.


.. py:function:: heatmap_for_median_expression(sample_file, labels, logic, level="Global", save=False, fname=None, dpi='figure', transform=z_score, title="", c_palette=sns.color_palette(['lightsteelblue', 'ivory', 'indianred'], 3), cmap_='vlag', dendrogram_ratio_=0.1)

   :param sample_data: sample data, where columns are the markers and rows ar the cells, the first column has ro be the Cell ID
   :type sample_data: pandas dataframe
   :param labels: the labels generated by TRIBUS
   :type labels: pandas dataframe
   :param logic:  the cell type discription table as a dictionary, where the keys are the levels and values are pandas dataframes, {str: pandas df}
   :type logic: dict
   :param level: which level of the labels do we want to visilaize, default will visualize the highest level
   :type level: str
   :param save: if True it save the plot with the given fname
   :type save: bool
   :param fname: the file name, if save=True
   :type fname: str

.. code-block:: python

    from tribus import heatmap_for_median_expression
    import pandas as pd

    sample_data = pd.read_csv(path)
    df_logic = pd.ExcelFile(path_logic)
    logic = pd.read_excel(df_logic, df.sheet_names, index_col=0)
    labels, _ = run_tribus(sample_data, logic)
    heatmap_for_median_expression(df, labels, logic)

.. image:: heatmap.png
   :width: 600

umap_vis
----------

This function performs dimension reduction using UMAP and then display the results colored by the markers and the labels
identified by TRIBUS

.. py:function:: umap_vis (sample_file, labels, markers, supervised=False level="Global", save=False, fname=None, title=None, init='spectral', random_state=0, n_neighbors=5, min_dist=0.1, metric='correlation', palette_markers='mycolormap', palette_cell='tab10', point_size=1,  dpi='figure')

   :param sample_data: sample data, where columns are the markers and rows ar the cells, the first column has ro be the Cell ID
   :type sample_data: pandas dataframe
   :param labels: the labels generated by TRIBUS
   :type labels: pandas dataframe
   :param markers: list of the markers, which we would like to plot the correlation inbetween, if None, it will visualize all the columns in sample data
   :type markers: list[str]
   :param supervised: if True, then it'll use the labels to calculate the dimension reduction
   :type supervised: bool
   :param level: which level of the labels do we want to visilaize, default will visualize the highest level
   :type level: str
   :param save: if True it save the plot with the given fname
   :type save: bool
   :param fname: the file name, if save=True
   :type fname: str

.. code-block:: python

    from tribus import umap_vis
    import pandas as pd

    sample_data = pd.read_csv(path)
    markers = sample_data.columns()
    df_logic = pd.ExcelFile(path_logic)
    logic = pd.read_excel(df_logic, df.sheet_names, index_col=0)
    labels, _ = run_tribus(sample_data, logic)
    umap_vis(df, labels, markers)

.. image:: umap.png
   :width: 600

cell_type_distribution
------------------------

The function plots a simple barplot about the distribution of the cell types in the results.

.. py:function:: cell_type_distribution(labels, level="Global", save=False, fname=None, dpi="Figure")

   :param labels: the labels generated by TRIBUS
   :type labels: pandas dataframe
   :param level: which level of the labels do we want to visilaize, default will visualize the highest level
   :type level: str
   :param save: if True it save the plot with the given fname
   :type save: bool
   :param fname: the file name, if save=True
   :type fname: str

.. code-block:: python

    from tribus import cell_type_distribution
    import pandas as pd

    sample_data = pd.read_csv(path)
    markers = sample_data.columns()
    df_logic = pd.ExcelFile(path_logic)
    logic = pd.read_excel(df_logic, df.sheet_names, index_col=0)
    labels, _ = run_tribus(sample_data, logic)
    cell_type_distribution(labels)



Normalizations
===============

Normalize data on each level

