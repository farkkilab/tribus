'''help validate inputs for main'''
import os, sys, datetime, shutil
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
    # TODO: list files in folder. Assume that all files are intended for analysis
    #   file names are sample names. possibility of using regex later on to get sample names
    #   check that all headers are the same
    #   return list of columns available
    return(True)

def validateGateLogic(excel_file):
    df = pd.ExcelFile(excel_file)
    logic = pd.read_excel(df, df.sheet_names, index_col=0)
    # TODO: navigate tabs and column names to make the lineage tree
    return(logic)

def validateInputs(input_folder, excel_file):
    """Called by tribus.py"""
    return(validateInputData(input_folder), validateGateLogic(excel_file))

def runClassify(path_in, logic, output_folder, depth):
    filenames=os.listdir(path_in)
    for samplefile in filenames:
        if samplefile.startswith('.'):
            continue
        print(samplefile)
        input_path = os.path.join(path_in,samplefile)
        if depth > 0:
            # TODO: test if other folders exist in 'args.output'
            #       if the logic.xlsx file remains unchanged for consecutive levels (tabs) load the results
            #
            #TODO: if previous labels exist find path for this command previous_labels = pd.read_csv(path_to_previous_result_file)
            # if we want to redo all the calls for all the levels from 0 to depth then keep it as None
            levels = range(0, depth)
            previous_labels = None
        elif depth == 0:
            # Runs only global cell types
            levels = [0]
            previous_labels = None
        else:
            return(False)
        # This call launches all the logic for one sample file
        result_labels = classify.run(input_path,logic,output_folder, levels, previous_labels)
        # write CSVs inside a new labels folder, one file per sample
        #with open(output_folder + os.sep + 'labels_' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M') + '.csv', 'w') as f:
        with open(output_folder + os.sep + 'labels_' + samplefile, 'w') as f:
            f.write("\n".join(result_labels))
    return(True)



# future: check output folder for existing labels, have they changed? which ones changed?
