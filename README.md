# Tribus: **Semi-automated panel-informed discovery of cell identities and phenotypes from multiplexed imaging and proteomic data**![img](./figures/Tribus_workflow.png)

## Installation

* For setting up conda environment, please use ``tribus_environment.yml`` to install all the dependencies. Run in conda prompt window:

```
conda env create --file=tribus_environment.yml
# This environment allows you to run Tribus and repeat all the analyzes in the manuscript. 
```

* Clone from GitHub repository.
* Then, run the following command in your conda environment of Tribus:

```
conda activate tribus

cd tribus/
python setup.py develop
pip install  -e ./
```

Now you are ready to use Tribus!

## Usage instructions

### Tribus for cell type classification

* We provide a jupyter notebook example. Please see example `Tribus_run.ipynb`.
* Datasets included in the manuscript and the corresponding scripts could be downloaded from Synapse with ID: `syn53754523`.

#### Input dataset

* Tribus requires an input dataset following the template below.
* No need to remove columns which are unused for cell type calling, Tribus will only read in the columns that you specified in the logic table.
* You can even include morphological features in the logic table, such as eccentricity or cell area, as long as it is helpful for the cell type calling.

| CellID | Marker 1 | Marker 2 | ... | Marker N | **Eccentricity** | Cell Area |
| ------ | -------- | -------- | --- | -------- | ---------------------- | --------- |
| 1      |          |          | ... |          |                        |           |
| 2      |          |          | ... |          |                        |           |

#### Logic table

Here is an example of 1-level logic table. The logic table is designed based on the marker panel following some rules: 

* If a marker should be present in a specific cell type, the value in the logic table needs to be assigned by 1. If a marker is supposed to be absent in a specific cell type, then the value in the logic table should be assigned -1. For neutral or unknown markers, 0 should be assigned.
* You can contain a marker will all 0, if you want to include this marker but uncertain with the present/absent of the marker.
* One cell type should have at least one positive marker among the whole logic table.

| Marker   | Cancer | Stromal | CD.4.Tcell | CD8.T.cell | CD11c.Myeloid | IBA1.Myeloid |
| -------- | ------ | ------- | ---------- | ---------- | ------------- | ------------ |
| CK7      | 1      | -1      | -1         | -1         | -1            | -1           |
| PAX8     | 1      | 0       | 0          | 0          | 0             | 0            |
| Vimentin | -1     | 1       | 0          | 0          | 0             | 0            |
| CD4      | 0      | -1      | 1          | -1         | -1            | -1           |
| CD8a     | 0      | -1      | -1         | 1          | -1            | -1           |
| IBA1     | 0      | 0       | 0          | 0          | 0             | 1            |
| CD11c    | 0      | 0       | 0          | 0          | 1             | 0            |

#### Tribus Parameter

```
# set random seed to ensure reproducity
depth = 1
labels, scores = tribus.run_tribus(np.arcsinh(sample_data[cols]/5.0), logic, depth=depth, normalization=z_score, 
                            tuning=0, sigma=1, learning_rate=1, 
                            clustering_threshold=100, undefined_threshold=0.0005, other_threshold=0.4, random_state=42)
```

* `depth`: levels of the logic table. You can set depth smaller than the levels you have - in this case Tribus will stop at the level as you wish.
* `normalization`: z_score or None
* `tuning`: When you set a number here, Tribus will run hyperparameter optimization with [number] rounds of repeat for `sigma` and `learning rate`. If you set 0, Tribus will not do hyperparameter optimization. We recommend you use hyperparameter optimization if you are not satisfied with the result and don't know how to adjust `sigma` and `learning rate`.
* `sigma`: is the radius of the different neighbors in the SOM. The default value for this is 1.0.
* `learning_rate`: determines how much weights are adjusted during each iteration.
* `clustering_threshold`: If the number of cells is smaller than the threshold you set here, Tribus will skip the SOM clustering and calculate the scoring function in single-cell level.
* `undefined_threshold`: if the difference between the maximum and second maximum score is smaller than the threshold, the cluster will be labeled as "undefined_[level_name]".
* `other_threshold`: if maximum score of a cluster is smaller than the threshold, the cluster will be labeled as the "other"
* `random_state`: None or any random seeds you like. To ensure the reproducity of your result :)

#### Tribus visualization

Tribus provide some visualization functions. You can find examples in example `Tribus_run.ipynb` in this repository.

* `marker_expression`: allows you to visualize the marker expression. You can evaluate the quality of the marker by checking this plot. ![img](./figures/Marker_expression.png)
* `cell_type_distribution`: Allows you to check the distribution of the cell types and evaluate the quality of the cell type calling result. ![img](./figures/Celltype_barplot.png)
* `heatmap_for_median_expression`: Draw a heatmap and allows you to check the marker expression in each cell type. ![img](./figures/Celltype_heatmap.png)

#### Napari plugin for fast user interaction

We provide ` Fast_masking_v2_colors_fixed.ipynb` to run Napari plugin. Run the chunks in the notebook and a napari window will pop out. You can check the quality of cell type calling and adjust the logic table correspondingly. 

![img](./figures/napari_interface.png)

We are also providing an Napari interface to run Tribus (function under testing now)! Here is the full interface. 

![img](./figures/napari_full.JPG)

## Folder structure

Here is an example of folder structure:
P.S. The input data and gate logic could be anywhere else in the computer as long as we specify the correct path when running Tribus.

```
    cool_project_name/
    |_ date_logic.xlsx
    |_ input_data/
    |   |_ each file here belongs to a separate slide (windsord-normalization is done by slide)
    |_ tribus_results/
        |_ 2021-11-02_13-40/
        |    |_ gates_2021-11-02_13-40.xlsx
        |    |_ labels_2021-11-02_13-40.csv
        |_ 2021-11-02_13-12/
            |_ gates_2021-11-02_13-12.xlsx
            |_ labels_2021-11-02_13-12.csv
```

## Citing Tribus

If you used Tribus in your research, please consider cite us: [https://doi.org/10.1101/2024.03.13.584767](https://doi.org/10.1101/2024.03.13.584767)
