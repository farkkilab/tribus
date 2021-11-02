# tribus package

## Installation

## Usage instructions

tribus preview <options> <paths>

tribus classify <options> <paths>
example: `tribus classify -i input_data/ -l gate_logic.xlsx -o tribus_results`

tribus report <options> <paths>

tribus napari <options> <paths>

tribus neighbors <options> <paths>

## Folder structure

Example of a project folder after using the `tribus classify` command:
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
