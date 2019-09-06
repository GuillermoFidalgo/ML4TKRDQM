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

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library

from wbmcrawlr.urls import WBM_URL

standard_library.install_aliases()
import cernrequests
import xmltodict
from cernrequests import get_sso_cookies


def _get_resource(servlet, parameters, cookies=None):
    if "FORMAT" not in parameters:
        parameters["FORMAT"] = "XML"

    params = "&".join(["{}={}".format(key, value) for key, value in parameters.items()])
    url = "{base}{servlet}?{params}".format(
        base=WBM_URL, servlet=servlet, params=params
    )

    if not cookies:
        cookies = get_sso_cookies(url, verify=False)

    response = cernrequests.get(url, cookies=cookies, verify=False)
    return xmltodict.parse(response.content)


def _get_run_summary(parameters):
    return _get_resource("RunSummary", parameters)


def get_run_summary(run_number):
    return _get_run_summary({"RUN": run_number})


def get_run_summary_by_range(run_number_from, run_number_to):
    return _get_run_summary({"RUN_BEGIN": run_number_from, "RUN_END": run_number_to})
