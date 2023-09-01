Get started
============

Install TRIBUS via pip:

.. code-block:: console

    $ pip install tribus

Install TRIBUS in Conda environment:

.. code-block:: console

     $ conda install tribus

Inputs
----------------

Tribus uses two tables as inputs. The first one is the data itself, on which we would like to perform the
cell-type annotation. The second one describes the cell types what we expect to be present in our data.
The cell-types are described by values [-1, 0, 1], which represents the expected markers expressions in one
particular cell-types. The cell-type annotation is hierarchical, which means first we can define higher level cell-types
and then we can split them into more detailed categories. An example of a lineage tree can be seen below,
which shows how the hierarchical clustering is done.

.. image:: lineage_tree.png
   :width: 600

**Sample data (csv):**

Contains the quantification data from the images. Columns should contain the markers and rows should
contain the cells. The first column has to contain IDs for the cells and the ID has to be unique. The table can contain columns which are
not part of the analysis (like X and Y coordinates of the cell), TRIBUS will filter the table to use only the
necessary markers.

.. code-block:: python

    sample_data.head()

.. csv-table:: Sample data
   :file: /Users/farateod/Documents/GitHub/tribus/docs/source/mock_data.csv
   :widths: auto
   :stub-columns: 1
   :header-rows: 1

**Cell type description table (xlsx):**

Contains the description of each expected cell-types. Examaple data:

.. list-table::
   :widths: auto
   :stub-columns: 1
   :header-rows: 1

   * - Markers
     - Cell-type1
     - Cell-type2
     - Cell-type3
     - Cell-type4
   * - Marker1
     - 1
     - 0
     - 0
     - -1
   * - Marker2
     - -1
     - -1
     - 0
     - 1
   * - Marker3
     - 1
     - 0
     - 0
     - 0
   * - Marker4
     - 0
     - 1
     - 0
     - -1
   * - Marker5
     - 0
     - -1
     - 1
     - 0

Each node in the lineage tree has to be a separate sheet in the xlsx file.
The first sheet always called: "Global", the follwoing sheets called as the corresponding higher level cell-type.
Some rules have to be considered, when we design the table:

- All cell types names have to be unique across all the level
- All level names (except the 1st level) have to apper in a previous level as a cell-type
- The sheet has to be in the right order in the xlsx file (Global, first level' sheets, second level's sheets, etc.)
- all cell-type has to have at least one positive (1) marker score
- That markers which are used in the table have to be in the sample data

An example of the cell-type description table can be found here:


Using Tribus
============

For this tutorial, we are providing an example dataset and cell-type description table, to perform the cell-type annotation,
and to familiarize yourself with the possibilities of the Tribus package. High-Grade-serus ovarian cancer, after the
chemotherapy. The data is produced by the CyCIF technology, segmentation, quantification, quality control is perfromed.
We suggest to preform proper quality control on the images, by cutting out blured, over-expressed
regions from the whole-slide images.

First of all let´s load all the required packages and functions

.. code-block:: python

    from tribus import correlation_matrix, marker_expression, log_zscore_normalization
    import pandas as pd

Data exploration and preprocessing
-----------------------------------

We provide some visulaization functions to explore the quantification data. First, you can
display the correlations-between markers. In an ideal data the markers describing the same cell-type, should
be highly correlated.

**Read-in the sample file and visualize the correlation matrix:**

.. code-block:: python

    sample = pd.read_csv(path, index_col=0)
    markers = sample.columns
    correlation_matrix(sample, markers)

.. image:: corr_matrix_new.png
   :width: 600

Furthermore, it is possible to visualize the distribution of the expression values of each markers. It helps to evaluate,
if there are still outliers, which marker has a bad quality etc.

**Visualize the marker's expression values:**

.. code-block:: python

    marker_expression(sample, markers)

.. image:: marker_expression.png
   :width: 600

We recommend to normalize the input data, before performing the cell type calling. For this we suggest to perform
log-normalization, and after the log-normalized data use z-score normalization. We provide a function, which performs
these two step together. However, it has to be noted, that not all dataset is unique, so it is possible, that another
type of normalization works better.

**Normalize the data:**

.. code-block:: python

    normalized_sample = log_zscore_normalization(sample)

**Let's visualize again the data, and check if it become nicer after the normalization:**

.. code-block:: python

    marker_expression(sample, markers)

.. image:: marker_expression.png
   :width: 600

.. code-block:: python

    correlation_matrix(sample, markers)

.. image:: corr_matrix_new.png
   :width: 600

Cell type annotation
----------------------

Then we can start the actual analysis. We should load the cell type description table into a dictionary, where keys are the
level-names and values are the actual dataframes. The first level always has to be names "Global". In the dataframes the
columns are the cell type names and the rows are the marker names. For further requeriments of the cell type description table can be
found here.

**Load the cell type description table:**

.. code-block:: python

    df = pd.ExcelFile("logic.xlsx")
    logic = pd.read_excel(df, df.sheet_names, index_col=0)

**Perform the cell type annotation with Tribus:**

.. code-block:: python

    labels, scores = run_tribus(normalized_sample, logic)

The labels dataframes contains the assigned labels on each level and also the final labels, from the lowest level.
There can occur labels like "other" and "undefined". Tribus gives the desciption "other", if the score is too low for
each cell types. It assigns "undefined" if the highest score for a cell-type is too close to the second-highest score, so the
assignment would be uncertain.

Analysing the results
----------------------
The very best way to evaluate the results is to look the images using Napari image viewer tool with its Tribus plug-in
displaying the labels on the image. The tutorial for Napari and Tribus can be found here. But we also provide further diagnostic plots
to help to evaluate the annotation.

The most powerful plot in the module is out heatmap,it is a big help in the evaluation of the results.
It shows the median expression of each marker among the cell type, while it also display the cell-type description table,
so it is easy to compare the results with the expected values. The median expression values are z-score normalized by markers
to make the plot more descriptive.

**Let's display the heatmap:**

.. code-block:: python

    heatmap_for_median_expression(normalized_sample, labels, logic)

.. image:: heatmap.png
   :width: 600

The next thing to check how many cells are in each cell type categories. For this we can use the built-in function
$cell_type_distribution()$.

**Number of cells in cell type categories:**

.. code-block:: python

    cell_type_distribution(labels)

.. image:: cell_type_distr.png
   :width: 600

You can also perform dimension reduction on the data to visualize it using UMAP. In this way we can check how good was the
clustering and how well separated the different cell types. Tribus provides a function for visualization, it colors the UMAP
by each marker expression and cell types, so it is easier to evaluate if ech cell types has the correct markers highly expressed.
There is an option, to use semi-supervised UMAP, which uses the the Tribus-cell-type labels to perform the dimension reduction,
which makes the evaluation even more efficient.

**First, let's take a look to the normal, unsupervised UMAP visualisation:**

.. code-block:: python

    umap_vis(sample_file, labels)

.. image:: umap.png
   :width: 600

**Then visualize the supervised UMAP:**
.. code-block:: python

    umap_vis(sample_file, labels, supervised=False)

.. image:: umap.png
   :width: 600

