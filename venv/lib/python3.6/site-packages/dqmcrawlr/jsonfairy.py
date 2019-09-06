import cernrequests
import re

from dqmcrawlr.exceptions import JSONNotFound

_BASE_URL = "https://cmsweb.cern.ch/dqm/{service}/jsonfairy/archive/"


def construct_url(run_number, dataset, resource, service):
    base_url = _BASE_URL.format(service=service)
    return "{}{}{}{}".format(base_url, run_number, dataset, resource)


def get_json(run_number, dataset, resource, service):
    """
    :param run_number: run number
    :param dataset: full dataset name
    :param resource: path of the plot
    :param service: "online" or "offline"
    :return:
    """
    url = construct_url(run_number, dataset, resource, service)
    json_response = cernrequests.get(url).json()

    if json_response["hist"] == "unsupported type":
        plot_name = re.search(r"\w+$", resource).group(0)
        raise JSONNotFound(
            "Unable to find plot '{}' for run '{}'".format(plot_name, run_number)
        )

    return json_response
