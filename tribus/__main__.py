'''
Tribus provides an interface to optimize the steps of a complete cell type calling process from highly multiplexed imaging data in settings where ground truth is not a possibility.

1. `tribus labels` assigns cell type labels to single cell data following a user description of how each cell type should "look".
2. `tribus browse` launches an interactive visualization of the cell type labels across samples and helps assessing the quality of the calls with prior knowledge.
3. `tribus report` will produce static figures and CSV files to be used as supplementary material or in downstream analyses.
'''

import os
import argparse
import subprocess
import pkg_resources

from . import utils, info

def f_napari(args: argparse.Namespace):
    utils.launch_napari(args.buttons)

def f_label(args: argparse.Namespace):
    utils.set_labels(args.paths)


def f_browse(args: argparse.Namespace):
    utils.browse_results(args.repo[0], args.new_name)


def f_report(args: argparse.Namespace):
    """
    TODO document all functions, these are just examples of posible ways of using the command line parameters (from another package)
    """
    if args.group:  # some variable in args
        label_sets = utils.get_sets()[args.group]
        sets = {k: repos[k] for k in label_sets if k in repos}
    for line in utils.describe(repos):
        print(line)


def main(argv=None):
    p = argparse.ArgumentParser(prog='tribus',
                                formatter_class=argparse.RawTextHelpFormatter,
                                description=__doc__)
    subparsers = p.add_subparsers(title='sub-commands',
                                  help='additional help with sub-command -h')

    version = pkg_resources.require('tribus')[0].version
    p.add_argument('-v',
                   '--version',
                   action='version',
                   version=f'%(prog)s {version}')

    # How to add options to a command
    p_label = subparsers.add_parser('label', help='label a repo')
    p_label.add_argument(
        'some_param',
        nargs=1,
        choices=utils.get_options_for_this_param(),
        help="label help with this argument")
    p_label.add_argument(
        'param2',
        help="new name")
    p_label.set_defaults(func=f_label)


if __name__ == '__main__':
    main()  # pragma: no cover