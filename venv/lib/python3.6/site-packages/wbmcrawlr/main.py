#!/usr/bin/python
# -*- coding: utf-8 -*-

# © Copyright 2018 CERN
#
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file “LICENSE”
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from future import standard_library

standard_library.install_aliases()
import argparse
import json

from wbmcrawlr import oms
from wbmcrawlr.utils import save_to_disk, check_oms_connectivity, get_oms_cookie


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="CERN CMS WBM and OMS crawler.",
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=36),
    )

    parser.add_argument(
        "--split-filling-scheme",
        help="Splits the filling scheme string into multiple fields",
        action="store_true",
    )

    resource_group = parser.add_mutually_exclusive_group(required=True)
    resource_group.add_argument(
        "--runs", metavar=("min", "max"), nargs=2, type=int, help="Retrieve Runs"
    )
    resource_group.add_argument(
        "--fills", metavar=("min", "max"), nargs=2, type=int, help="Retrieve Fills"
    )
    resource_group.add_argument(
        "--lumisections", metavar="run", nargs=1, type=int, help="Retrieve Lumisections"
    )
    resource_group.add_argument(
        "--hltrates",
        metavar=("run", "path_name"),
        nargs=2,
        help="Hlt rates for given path per lumisection",
    )
    resource_group.add_argument(
        "--all-hltrates",
        metavar="run",
        nargs=1,
        type=int,
        help="Hlt rates for all available paths per lumisection",
    )

    return parser.parse_args()


def main():

    args = parse_arguments()

    if args.runs:
        resource_name = "runs"
        method = oms.get_runs
        arguments = args.runs
    elif args.fills:
        resource_name = "fills"
        method = oms.get_fills
        arguments = args.fills
    elif args.lumisections:
        resource_name = "lumisections"
        method = oms.get_lumisections
        arguments = args.lumisections
    elif args.hltrates:
        resource_name = "hltrates"
        method = oms.get_hltpathrates
        arguments = args.hltrates
    elif args.all_hltrates:
        resource_name = "hltrates"
        method = oms.get_all_hltpathrates
        arguments = args.all_hltrates
    else:
        raise NotImplementedError

    kwargs = {}

    if not check_oms_connectivity():
        kwargs["inside_cern_gpn"] = False
        kwargs["cookies"] = get_oms_cookie()

    extra_arguments = {}

    if args.split_filling_scheme and args.fills:
        extra_arguments['split_filling_scheme'] = True

    response = method(*arguments, **kwargs, **extra_arguments)

    content = json.dumps(response, indent=2)

    filename = "oms_{}.json".format(resource_name)
    save_to_disk(filename, content=content)
    print("Stored {} {} in '{}'".format(len(response), resource_name, filename))


if __name__ == "__main__":
    main()
