# Tribus: **Semi-automated panel-informed discovery of cell identities and phenotypes from multiplexed imaging and proteomic data**![img](./Tribus_workflow.png)

## Installation

* For setting up conda environment, please use ``tribus_environment.yml`` to install all the dependencies. Run in conda prompt window:

```
conda env create --file=tribus_environment.yml
# This environment allows you to run Tribus and repeat all the analyzes in the manuscript. 
```

* We also provide a simplified environment `tribus_lightenv.yml` to run Tribus.
* Clone from GitHub repository and run the following command in your conda environment of Tribus:

```
conda activate tribus

cd tribus/
python setup.py develop
pip install  -e ./
```

Now you are ready to use Tribus!

## Usage instructions

### Tribus for cell type classification

* We provide a jupyter notebook example. Please see example here: (coming soon)
* Example datasets and more scripts could be downloaded from Synapse: (link coming soon)

#### Input dataset

#### Logic table

#### Tribus visualization

#### Napari plugin for fast user interaction

We provide ` Fast_masking_v2_colors_fixed.ipynb` to run Napari plugin. 

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
