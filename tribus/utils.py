import os, sys, datetime, shutil
from . import classify
from . import label_logic
import numpy as np
import pandas as pd
import networkx as nx
import math
import time


# create output folder
# check channel names
# check label logic
# count all requirements present
# levels of calls
# parse the table into a better structure, list? array? dict?

def read_input_files(input_folder):
    sample_files = {}
    filenames = os.listdir(input_folder)
    for file in filenames:
        if file.startswith('.'):
            continue

        input_path = os.path.join(input_folder, file)
        df = pd.read_csv(input_path, index_col=0)
        sample_files[file] = df

    return sample_files


def validate_input_data(file, logic):
    # TODO: list files in folder. Assume that all files are intended for analysis
    #   file names are sample names. possibility of using regex later on to get sample names
    #   check that all headers are the same

    valid = True
    markers_in_logic = np.unique([marker for key in logic for marker in logic[key].index])
    if len(file.index) != len(np.unique(file.index)):
        valid = False
        print(f"Cell Ids are not unique in file {file}")

    # Validate if all marker in the input data
    for marker in markers_in_logic:
        if marker not in file.columns:
            valid = False
            print("not all marker are present in the input data")

    return valid


def build_tree_(logic, graph, sheet_name, sheet_names, depth, current_depth):
    # TODO new termination state??
    if current_depth > depth:
        return
    sheet = logic[sheet_name]
    cell_types = sheet.columns
    for i in cell_types:
        if i in sheet_names:
            graph.add_edge(sheet_name, i)
            build_tree_(logic, graph, i, sheet_names, depth, current_depth + 1)


def build_tree(logic, depth):
    # create the lineage tree from levels
    graph = nx.DiGraph()
    sheet_names = list(logic.keys())
    graph.add_node(sheet_names[0])
    build_tree_(logic, graph, sheet_names[0], sheet_names, depth, 1)
    return graph


def read_logic(excel_file):
    df = pd.ExcelFile(excel_file)
    logic = pd.read_excel(df, df.sheet_names, index_col=0)
    return logic


def validate_gate_logic(logic):
    valid = True
    if len(logic.keys()) != len(np.unique(list(logic.keys()))):
        valid = False
        print("The cell type names are not unique")

    all_cell_type = []
    for key in logic:
        if all_cell_type:
            if key not in all_cell_type:
                valid = False
                print(f"{key} is not present in previous cell type description table")
        for c in logic[key].columns:
            all_cell_type.append(c)
            if 1 not in list(logic[key][c]):
                valid = False
                print(f"No positive marker for cell-type {c}")

    return valid


def validate_inputs(input_files, logic):
    valid_logic = validate_gate_logic(logic)

    valid_input = True

    for df in input_files:
        if not validate_input_data(df, logic):
            valid_input = False

    if valid_input and valid_logic:
        valid = True
    else:
        valid = False
    return valid


def traverse(graph, node, old_logic, logic, previous_labels, reusable_labels, old_levels):
    if node in old_levels and old_logic[node].equals(logic[node]) and node in previous_labels.columns:
        reusable_labels[node] = previous_labels[node]
        out_edges = graph.out_edges(node)
        for i, j in out_edges:
            traverse(graph, j, old_logic, logic, previous_labels, reusable_labels, old_levels)


def re_entry(output, logic, depth, sample_name, tree, output_folder):
    folders = []
    reusable_labels = pd.DataFrame()
    for path in os.listdir(output):
        if not os.path.isfile(os.path.join(output, path)) and path != output_folder.split("/")[-1]:
            folders.append(path)

    if len(folders) == 0:
        print('len(folders)==0')
        return reusable_labels
    else:
        folders = sorted(folders, reverse=True)
        folder = folders[0]
        previous_labels = pd.read_csv(f'{output}/{folder}/labels_{sample_name}')
        df = pd.ExcelFile(f'{output}/{folder}/expected_phenotypes.xlsx')
        old_levels = df.sheet_names
        old_logic = pd.read_excel(df, df.sheet_names, index_col=0)

        traverse(tree, 'Global', old_logic, logic, previous_labels, reusable_labels, old_levels)
        return reusable_labels


def run_classify(input_files, logic, output_folder, depth, output, tree):
    for file in input_files:
        if depth < 0:
            previous_labels = re_entry(output, logic, depth, file, tree, output_folder)
        else:
            previous_labels = pd.DataFrame()

        start = time.time()
        result_labels, prob_table = classify.run(input_files[file], logic, depth, previous_labels, tree)
        end = time.time()
        print(end - start)

        # write CSVs inside a new labels folder, one file per sample
        result_labels.to_csv(f'{output_folder}{os.sep}labels_{file}')
        prob_table.to_csv(f'{output_folder}{os.sep}prob_{file}')
    return True

