# _tribus_ package

## Installation (internal instructions on developing and testing a pip package)

```
   cd tribus/
   python setup.py develop
   pip install  -e ./
```

## Usage instructions

We recommend feeding it data that is already log-transformed or at least not too skewed.

### tribus preview <options> <paths>
    
    Not yet in the plans, could be a future branch from report (without labels)

### tribus classify <options> <paths>
    
Example for running the labeling module:
```
    cd ../cool_project_name
    tribus classify -i input_data/ -l gate_logic.xlsx -o tribus_results
```

### tribus report <options> <paths>

    TODO instructions to open the interactive report
    
### tribus napari <options> <paths>
    
    TODO instructions to open the napari viewer with the labels. Where should masks and images be?

### tribus neighbors <options> <paths>

    TODO implement quick computation of spatial features to add to the labels afterwards.
    
## Folder structure

Example of my test folder after using the `tribus classify` command:
the input data and gate logic could be anywhere else in the computer as long as we put the correct path.
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
