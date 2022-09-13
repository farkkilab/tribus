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

def reEntry(output_folder, logic, depth, sample_name):
    folders = []
    reUssableLabels = pd.DataFrame()
    similarities = []
    for path in os.listdir(output_folder):
        if not os.path.isfile(os.path.join(output_folder, path)):
            folders.append(path)

    if len(folders) == 0:
        print('len(folders)==0')
        return None
    else:
        folders = sorted(folders, reverse = True)
        for folder in folders:
            df = pd.ExcelFile(f'{output_folder}/{folder}/expected_phenotypes.xlsx')
            old_logic = pd.read_excel(df, df.sheet_names, index_col=0)
            levels = list(logic.keys())
            current_similarity = 0
            for i in range(depth):
                if not levels[i] in old_logic.keys():
                   return None #TODO return with the current state of labels
                else:
                    if old_logic[levels[i]] == logic[levels[i]]:
                        current_similarity = i

            similarities.append(current_similarity)

        best_match = folders[np.argmax(similarities)]
        previous_labels = pd.read_csv(f'{output_folder}/{best_match}/labels_{sample_name}')
        for i in range(depth):
            if not levels[i] in old_logic.keys():
                return None  # TODO return with the current state of labels
            else:
                if old_logic[levels[i]] == logic[levels[i]]:
                    reUssableLabels[levels[i]] = previous_labels[levels[i]]

        return reUssableLabels

def runClassify(path_in, logic, output_folder, depth, output):
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
            previous_labels = reEntry(output, logic, depth)
        elif depth == 0:
            # Runs only global cell types
            levels = [0]
            previous_labels = None
        else:
            return(False)
        # This call launches all the logic for one sample file
        result_labels = classify.run(samplefile, input_path,logic,output_folder, levels, previous_labels)
        # write CSVs inside a new labels folder, one file per sample
        result_labels.to_csv(f'{output_folder}{os.sep}labels_{samplefile}')
        #with open(output_folder + os.sep + 'labels_' + samplefile, 'w') as f:
            #f.write("\n".join(result_labels))
    return(True)



# future: check output folder for existing labels, have they changed? which ones changed?
