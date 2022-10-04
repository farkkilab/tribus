'''help validate inputs for main'''
import os, sys, datetime, shutil
from . import classify
from . import label_logic
import numpy as np
import pandas as pd
import networkx as nx


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

def buildTree(file, graph, sheet_name, sheet_names, depth, current_depth):
    if current_depth > depth:
        return
    sheet = pd.read_excel(file, sheet_name=sheet_name)
    cell_types = sheet.columns[1:]
    for i in cell_types:
        if i in sheet_names:
            graph.add_edge(sheet_name, i)
            buildTree(file, graph, i, sheet_names, depth, current_depth+1)

#create a the lineage tree from levels
def buildTree_from_file(file, depth):
    graph = nx.DiGraph()
    xl = pd.ExcelFile(file)
    sheet_names = xl.sheet_names
    graph.add_node(sheet_names[0])
    buildTree(file, graph, sheet_names[0], sheet_names, depth, 1)
    return graph


def validateGateLogic(excel_file, depth):
    df = pd.ExcelFile(excel_file)
    logic = pd.read_excel(df, df.sheet_names, index_col=0)
    tree = buildTree_from_file(excel_file, depth)
    # TODO: navigate tabs and column names to make the lineage tree
    return logic, tree

def validateInputs(input_folder, excel_file, depth):
    """Called by tribus.py"""
    logic, tree = validateGateLogic(excel_file, depth)
    return(validateInputData(input_folder), logic, tree)

def traverse(graph, node, old_logic, logic, previous_labels, reUssableLabels, old_levels):
    if node in old_levels and old_logic[node].equals(logic[node]) and node in previous_labels.columns:
        reUssableLabels[node] = previous_labels[node]
        out_edges = graph.out_edges(node)
        for i, j in out_edges:
            traverse(graph, j, old_logic, logic, previous_labels, reUssableLabels, old_levels)

def reEntry(output, logic, depth, sample_name, tree, output_folder):
    folders = []
    reUssableLabels = pd.DataFrame()
    for path in os.listdir(output):
        if not os.path.isfile(os.path.join(output, path)) and path != output_folder.split("/")[-1]:
            folders.append(path)

    if len(folders) == 0:
        print('len(folders)==0')
        return None
    else:
        folders = sorted(folders, reverse = True)
        folder = folders[0]
        previous_labels = pd.read_csv(f'{output}/{folder}/labels_{sample_name}')
        df = pd.ExcelFile(f'{output}/{folder}/expected_phenotypes.xlsx')
        old_levels = df.sheet_names
        old_logic = pd.read_excel(df, df.sheet_names, index_col=0)

        traverse(tree, 'Global', old_logic, logic, previous_labels, reUssableLabels, old_levels)
        #print(reUssableLabels)
        return reUssableLabels

def runClassify(path_in, logic, output_folder, depth, output, tree):
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
            previous_labels = reEntry(output, logic, depth, samplefile, tree, output_folder)
        elif depth == 0:
            # Runs only global cell types
            levels = [0]
            previous_labels = None
        else:
            return(False)
        # This call launches all the logic for one sample file
        result_labels = classify.run(samplefile, input_path,logic,output_folder, levels, previous_labels, tree)
        # write CSVs inside a new labels folder, one file per sample
        result_labels.to_csv(f'{output_folder}{os.sep}labels_{samplefile}')
        #with open(output_folder + os.sep + 'labels_' + samplefile, 'w') as f:
            #f.write("\n".join(result_labels))
    return(True)



# future: check output folder for existing labels, have they changed? which ones changed?
