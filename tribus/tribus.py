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

import math
import pandas as pd
import pkg_resources
from . import utils
from . import classify


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
            run_tribus_from_file(args.depth, args.logic, args.input, args.output)
            # store the logic file in this folder, so the user can always go back to see which logic created those results
            shutil.copy(args.logic, args.output + os.sep + 'expected_phenotypes' + '.xlsx')
        else:
            print('input paths are not a directory and a file.')
    elif args.command == 'preview':
        print('not implemented')
    elif args.command == 'report':
        print('not implemented')
    else:
        parser.print_help()


def run_tribus_from_file(depth, logic, input, output):
    valid_depth = True
    if depth < 0:
        valid_depth = depth >= 0
        print("Depth should be positive or zero")

    logic = utils.read_logic(logic)
    input_files = utils.read_input_files(input)
    valid = utils.validate_inputs(input_files, logic)

    if valid and valid_depth:
        tree = utils.build_tree(logic, depth)
        # create output dir if not present, and create a subfolder with current time stamp
        output_folder = os.path.join(output, datetime.datetime.now().strftime('%Y-%m-%d_%H-%M'))
        # Instruct the user to NOT EDIT ANY CONTENTS OF THE RESULT FOLDERS
        Path(output_folder).mkdir(parents=True, exist_ok=True)
        print('print output folder', output_folder)

        # This call does everything
        utils.run_classify(input_files, logic, output_folder, depth, output, tree)
    else:
        print('invalid data: check logs.')


def run_tribus(input_df, logic, depth=1):
    valid_depth = True
    if depth < 0:
        valid_depth = depth >= 0
        print("Depth should be positive or zero")

    valid_input = utils.validate_input_data(input_df, logic)
    valid_logic = utils.validate_gate_logic(logic)

    result_table, prob_table = pd.DataFrame()

    if valid_input and valid_logic and valid_depth:
        tree = utils.build_tree(logic, depth)
        result_table, prob_table = classify.run(input_df, logic, depth, pd.DataFrame(), tree)
    else:
        # TODO raise error
        print('invalid data: check logs.')

    return result_table, prob_table

#EOF