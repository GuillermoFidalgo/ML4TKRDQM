import os

import numpy
import pandas

from trackerstudies.filters import (
    exclude_online,
    exclude_commissioning,
    exclude_special,
    exclude_open,
)
from trackerstudies.settings import ENTROPY_CACHE_NAME
from .algorithms import reference_cost, angular_correlation_entropy
from .exceptions import TrackingMapNotFound
from .extract import extract_tracking_map_content
from .load import (
    load_tracking_map,
    load_tracker_runs,
    load_tkdqmdoctor_runs,
    load_oms_runs,
    load_global_runs,
    load_tkdqmdoctor_problem_runs,
    load_all_histogram_folders,
    load_online_tracker_runs,
    load_oms_fills,
    load_track_histograms,
)
from .merge import (
    merge_runreg_tkdqmdoc,
    merge_runreg_oms,
    merge_runreg_runreg,
    merge_runreg_tkdqmdoc_problem_runs,
    merge_runreg_histograms,
    merge_oms_runs_oms_fills,
)
from .pipes import (
    add_runtype,
    add_is_bad,
    add_reference_cost,
    add_is_heavy_ion,
    add_is_commissioning,
    add_is_special,
    add_all_problems,
    add_status_summary,
    add_bad_reason,
)


def calculate_tracking_map_reference_cost(run_number, reference_run_number, reco):
    try:
        tracking_map = load_tracking_map(run_number, reco)
        reference_map = load_tracking_map(reference_run_number, reco)
    except TrackingMapNotFound:
        # print("Cant find tracking map for {} {} ".format(row.run_number, row.reco))
        return numpy.nan
    except ValueError:
        # print("Incompatible Map for {} {} ".format(row.run_number, row.reco))
        return numpy.nan

    tracking_map_content = extract_tracking_map_content(tracking_map)
    reference_map_content = extract_tracking_map_content(reference_map)
    return reference_cost(tracking_map_content, reference_map_content)


def calculate_angular_entropy(run_number, reco):
    print(
        "Calculating angular tracking map entropy for '{}' ({})...".format(
            run_number, reco
        ),
        end="",
        flush=True,
    )
    try:
        tracking_map = load_tracking_map(run_number, reco)
    except TrackingMapNotFound:
        # print("Cant find tracking map for {} {} ".format(row.run_number, row.reco))
        print("Failed")
        return numpy.nan
    except ValueError:
        # print("Incompatible Map for {} {} ".format(row.run_number, row.reco))
        print("Failed")
        return numpy.nan

    tracking_map_content = extract_tracking_map_content(tracking_map)
    entropy = angular_correlation_entropy(tracking_map_content)
    print("OK")
    return entropy


def setup_pandas_display(max_rows=10, max_columns=10, width=10000):
    pandas.set_option("display.max_rows", max_rows)
    pandas.set_option("display.max_columns", max_columns)
    pandas.set_option("display.width", width)


def apply_everything(dataframe):
    return (
        dataframe.pipe(add_runtype)
        .pipe(add_is_bad)
        .pipe(add_reference_cost)
        .pipe(add_is_special)
        .pipe(add_is_commissioning)
        .pipe(add_is_heavy_ion)
        .pipe(exclude_commissioning)
        .pipe(exclude_special)
    )


def load_fully_setup_tracker_runs():
    tracker_runs = load_tracker_runs()
    tkdqmdoctor_runs = load_tkdqmdoctor_runs()
    oms_runs = load_oms_runs()

    return (
        tracker_runs.pipe(merge_runreg_tkdqmdoc, tkdqmdoctor_runs)
        .pipe(merge_runreg_oms, oms_runs)
        .pipe(exclude_online)
        .pipe(exclude_open)
        .pipe(apply_everything)
    )


def load_tracking_map_content(run_number, reco):
    tracking_map = load_tracking_map(run_number, reco)
    return extract_tracking_map_content(tracking_map)


def load_fully_setup_global_runs():
    global_runs = load_global_runs()
    tkdqmdoctor_runs = load_tkdqmdoctor_runs()
    oms_runs = load_oms_runs()

    return (
        global_runs.pipe(merge_runreg_tkdqmdoc, tkdqmdoctor_runs)
        .pipe(merge_runreg_oms, oms_runs)
        .pipe(exclude_online)
        .pipe(exclude_open)
        .pipe(apply_everything)
    )


def load_all_workspaces_full_setup():
    return merge_runreg_runreg(
        load_fully_setup_tracker_runs(), load_fully_setup_global_runs()
    )


def get_entropy_cache():
    return (
        pandas.read_pickle(ENTROPY_CACHE_NAME)
        if os.path.isfile(ENTROPY_CACHE_NAME)
        else pandas.DataFrame(
            columns=["run_number", "reco", "angular_entropy"]
        ).set_index(["run_number", "reco"])
    )


def save_entropy_cache(dataframe):
    dataframe.to_pickle(ENTROPY_CACHE_NAME)


def get_angular_entropy(run_number, reco, entropy_cache=None):
    try:
        return entropy_cache.loc[(run_number, reco), "angular_entropy"]
    except KeyError:
        entropy = calculate_angular_entropy(run_number, reco)
        entropy_cache.loc[(run_number, reco), "angular_entropy"] = entropy
        return entropy


def load_merged_tracker_runs():
    tracker_runs = load_tracker_runs()
    tkdqmdoctor_runs = load_tkdqmdoctor_runs()
    tkdqmdoctor_problem_runs = load_tkdqmdoctor_problem_runs()
    oms_runs = load_oms_runs()

    return (
        tracker_runs.pipe(merge_runreg_tkdqmdoc, tkdqmdoctor_runs)
        .pipe(merge_runreg_tkdqmdoc_problem_runs, tkdqmdoctor_problem_runs)
        .pipe(merge_runreg_oms, oms_runs)
    )


def add_all_columns(dataframe):
    return (
        dataframe.pipe(add_runtype)
        .pipe(add_is_bad)
        .pipe(add_reference_cost)
        .pipe(add_is_special)
        .pipe(add_is_commissioning)
        .pipe(add_is_heavy_ion)
        .pipe(add_all_problems)
    )


def load_runs(from_pickle=True):
    """
    Loads all runs from the Tracker workspace merged with:
     - OMS
     - TkDQMDoctor
     - DQM GUI Histograms
     - twiki TODO
     -

    Adding all sorts of additional column information.

    Excluding Commissioning, Special, Online and Open Runs
    :return:
    """
    pickle_path = os.path.join("data", "runs.pkl")
    try:
        if from_pickle:
            return pandas.read_pickle(pickle_path)
    except FileNotFoundError:
        pass

    tracker_runs = load_tracker_runs()
    tracker_online_runs = load_online_tracker_runs()
    tkdqmdoctor_runs = load_tkdqmdoctor_runs()
    tkdqmdoctor_problem_runs = load_tkdqmdoctor_problem_runs()
    oms_runs = load_oms_runs()
    oms_fills = load_oms_fills()
    oms_runs = merge_oms_runs_oms_fills(oms_runs, oms_fills)
    histograms = load_all_histogram_folders()

    runs = (
        tracker_runs.pipe(merge_runreg_runreg, tracker_online_runs)
        .pipe(merge_runreg_tkdqmdoc, tkdqmdoctor_runs)
        .pipe(merge_runreg_tkdqmdoc_problem_runs, tkdqmdoctor_problem_runs)
        .pipe(merge_runreg_oms, oms_runs)
        .pipe(merge_runreg_histograms, histograms)
        .pipe(add_runtype)
        .pipe(add_is_special)
        .pipe(add_is_commissioning)
        .pipe(exclude_commissioning)
        .pipe(exclude_special)
        .pipe(exclude_open)
        .pipe(add_is_bad)
        .pipe(add_is_heavy_ion)
        # .pipe(add_all_problems)
        .pipe(add_status_summary)
        .pipe(add_bad_reason)
    ).sort_values(by=["run_number", "reco"])

    # TODO .pipe(add_reference_cost)
    # TODO .pipe(add_angular_correlation_entropy)
    # TODO .pipe(add_scaled_reference_difference_sum)

    runs.to_pickle(pickle_path)
    return runs
