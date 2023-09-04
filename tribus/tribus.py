'''
Tribus provides an interface to optimize the steps of a complete cell type calling process from highly multiplexed imaging data in settings where ground truth is not a possibility.

1. `tribus classify` assigns cell type labels to single cell data following a user description of how each cell type should "look".
2. `tribus preview` launches an interactive visualization of the cell type labels across samples and helps assessing the quality of the calls with prior knowledge.
3. `tribus report` will produce static figures and CSV files to be used as supplementary material or in downstream analyses.
'''
# Potential feature:
# tribus generate-logic -i <input DIR>
#
###
# Test the package live on anaconda prompt with:
#   cd /tribus/
#   python setup.py develop
#   pip install  -e ./
#   cd ../test data
# tribus classify -i input_data/ -l gate_logic_1.xlsx -o test_results
#
#
###

import os, sys, datetime, shutil
import argparse
from pathlib import Path
import pandas as pd
import time
import pkg_resources
import utils
import classify
import xlsxwriter


def main(argv=None):
    parser = argparse.ArgumentParser(prog='tribus', description='Execute tribus options on single cell data tables')
    subparsers = parser.add_subparsers(title='tribus subcommands',help='Additional sub-command help with -h',dest='command')
    
    version = pkg_resources.require('tribus')[0].version
    parser.add_argument('--version',
        action='version',
        version=f'%(prog)s {version}')

    # Create one command for each use case
    parser_classify = subparsers.add_parser('classify', help='Assign cell type labels to cells')
    parser_preview = subparsers.add_parser('preview', help='Preview data with no labels')
    parser_report = subparsers.add_parser('report', help='Report quality metrics for cell type labels')
    # In the future also the neighbor calculations

    # Add parameters to each command
    parser_classify.add_argument('-i','--input', metavar='DIR',
        help='Folder containing CSV files, one per sample')
    parser_classify.add_argument('-l','--logic', metavar='XLSX',
        help='Excel file containing the prior knowledge of the markers and the cell type labels')
    parser_classify.add_argument('-d','--depth', metavar='N', type=int, default=0,
        help='Level of cell type calls, the number indicates the Excel tab in order. 0 only runs the first tab, 1 runs the first and second, and so on.')
    parser_classify.add_argument('-o','--output', metavar='DIR',
        help='Folder to store all results of multiple runs.')
    parser_preview.add_argument('-i','--input', metavar='DIR',
        help='Folder containing CSV files, one per sample')
    # Seems unused for now - consider removing later
    parser_report.add_argument('--resultFolder', metavar='DIR',
        help='Generate quality report after labeling')

    args = parser.parse_args(argv)
    
    if args.command == 'classify':
        if os.path.isfile(args.logic) and os.path.isdir(args.input):
            run_tribus_from_file(args.input, args.output, args.logic, args.depth)
            # store the logic file in this folder, so the user can always go back to see which logic created those results
        else:
            print('input paths are not a directory and a file.')
    elif args.command == 'preview':
        print('not implemented')
    elif args.command == 'report':
        print('not implemented')
    else:
        parser.print_help()


def run_tribus_from_file(input_path, output, logic_path, depth=1, save_figures=False, normalization=None, 
                         tuning=False, max_evals=15, sigma=.5, learning_rate=.5, clustering_threshold=15_000,
                         undefined_threshold=0.01, other_threshold=0.4, random_state=None):
    '''Running tribus on multiple samples
    input_path: string (path for the folder, which contains the sample files)
    output: string (path, where tribus will generate the output folder (named with timestamp) containing the results)
    logic_path: string (path for the logic file)
    depth: integer (how many levels should tribus run the analysis)
    save_figures: bool
    it will automatically save the results into the output folder
    '''

    valid_depth = True
    # check if input parameters are suitable
    if depth < 0:
        valid_depth = depth >= 0
        print("Depth should be positive or zero")

    logic = utils.read_logic(logic_path)
    input_files = utils.read_input_files(input_path)
    valid = utils.validate_inputs(input_files, logic)

    if valid and valid_depth:
        tree = utils.build_tree(logic, depth)
        # create output dir if not present, and create a subfolder with current time stamp
        output_folder = os.path.join(output, datetime.datetime.now().strftime('%Y-%m-%d_%H-%M'))
        # Instruct the user to NOT EDIT ANY CONTENTS OF THE RESULT FOLDERS
        Path(output_folder).mkdir(parents=True, exist_ok=True)

        #save the logic table, so the user will know what logic was used for which results
        writer = pd.ExcelWriter(f"{output_folder}/expected_phenotypes.xlsx", engine='xlsxwriter')
        for key in logic:
            logic[key].to_excel(writer, sheet_name=key)

        print('print output folder', output_folder)

        # This call does everything
        utils.run_classify(input_files, logic, output_folder, depth, output, tree, save_figures, normalization=normalization, tuning=tuning, max_evals=max_evals, 
                           sigma=sigma, learning_rate=learning_rate, clustering_threshold=clustering_threshold, undefined_threshold=undefined_threshold,
                           other_threshold=other_threshold, random_state=random_state)
    else:
        raise AssertionError('invalid data: check logs.')


def run_tribus(input_df, logic, depth=1, normalization=None, tuning=False, max_evals=15, sigma=.5, learning_rate=.5, clustering_threshold=15_000, undefined_threshold=0.01,
               other_threshold=0.4, random_state=None):
    valid_depth = True
    if depth < 0:
        valid_depth = depth >= 0
        print("Depth should be positive or zero")

    valid_input = utils.validate_input_data(input_df, logic)
    valid_logic = utils.validate_gate_logic(logic)

    result_table = pd.DataFrame()
    prob_table = pd.DataFrame()

    start = time.time()
    if valid_input and valid_logic and valid_depth:
        tree = utils.build_tree(logic, depth)
        result_table, prob_table = classify.run(input_df, logic, depth, pd.DataFrame(), tree, normalization=normalization,
                                                tuning=tuning, max_evals=max_evals, sigma=sigma, learning_rate=learning_rate, 
                                                clustering_threshold=clustering_threshold, undefined_threshold=undefined_threshold,
                                                other_threshold=other_threshold, random_state=random_state)
    else:
        # TODO raise error
        print('invalid data: check logs.')
    end = time.time()
    print((end - start) / 60, "minutes")

    return result_table, prob_table

#EOF