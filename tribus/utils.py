'''help validate inputs for main'''
from . import classify
from . import label_logic
import numpy as np
import pandas as pd


# create output folder
# check channel names
# check label logic
# count all requirements present
# levels of calls
# parse the table into a better structure, list? array? dict?


def validateInputData(input_folder):
    # list files in folder. Assume that all files are intended for analysis
    # file names are sample names. possibility of using regex later on to get sample names
    # check that all headers are the same
    # return list of columns available
    return(True)

def validateGateLogic(excel_file):
    df = pd.ExcelFile(excel_file)
    logic = pd.read_excel(df, df.sheet_names, index_col=0)
    # hardcoded immune matching?
    return(logic)

def validateInputs(input_folder, excel_file):
    """Called by tribus.py"""
    return(validateInputData(input_folder), validateGateLogic(excel_file))

def runClassify(path_in, logic, output_folder):
    # TODO: test if other folders exist in 'args.output' and if some 'level' in 'labels' was not changed (meanwhile it runs all the way regardless)

    result = classify.run(path_in,logic,output_folder)
    
    # write CSVs
    return(True)



# future: check output folder for existing labels, have they changed? which ones changed?