#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Pymatgen Development Team.
# Distributed under the terms of the MIT License.

"""
A master convenience script with many tools for vasp and structure analysis.
"""

import argparse
import sys
import itertools

from tabulate import tabulate, tabulate_formats
from pymatgen import Structure
from pathlib import Path
from megnet.utils.models import MEGNetModel


def predict(args):
    """
    Handle view commands.

    :param args: Args from command.
    """
    headers = ["Filename"]
    output = []
    models = []
    for mn in args.models:
        model = MEGNetModel.from_file(mn)
        models.append(model)
        headers.append("%s (%s)" % (mn, str(model.metadata["unit"]).strip("log10")))

    for fn in args.structures:
        structure = Structure.from_file(fn)
        row = [fn]
        for model in models:
            val = model.predict_structure(structure).ravel()
            if "log10" in str(model.metadata["unit"]):
                val = 10 ** val
            row.append(val)
        output.append(row)
    print(tabulate(output, headers=headers))


def main():
    """
    Handle main.
    """
    parser = argparse.ArgumentParser(
        description="""
    meg is command-line interface to useful MEGNet tasks, e.g., prediction
    using a built model, etc. To see the options for the
    sub-commands, type "meg sub-command -h"."""
    )

    subparsers = parser.add_subparsers()

    parser_predict = subparsers.add_parser(
        "predict", help="Predict property using MEGNET.")

    parser_predict.add_argument("-s", "--structures", dest="structures",
                                type=str, nargs="+",
                                help="Structures to process")
    parser_predict.add_argument(
        "-m", "--models", dest="models", type=str, nargs="+", required=True,
        help="Models to run.")
    parser_predict.set_defaults(func=predict)

    args = parser.parse_args()

    try:
        getattr(args, "func")
    except AttributeError:
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()