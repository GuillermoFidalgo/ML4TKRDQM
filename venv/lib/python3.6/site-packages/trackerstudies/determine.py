import numpy
import pandas


def determine_tracker_is_bad(pixel, strip, tracking, runtype):
    try:
        return (
            pixel.lower() != "good"
            and runtype.lower() == "collisions"
            or strip.lower() != "good"
            or tracking.lower() != "good"
        )
    except AttributeError:
        return numpy.nan


def determine_is_heavy_ion(rda_name):
    return "HI" in rda_name


def determine_is_commissioning(run_class_name, rda_name):
    return "Commissioning" in run_class_name or "Commiss" in rda_name


def determine_is_special(run_class_name, rda_name):
    return "Special" in run_class_name or "Special" in rda_name


def determine_is_collisions(run_class_name):
    return "Collisions" in run_class_name


def determine_is_cosmics(run_class_name):
    return "Cosmics" in run_class_name


def determine_runtype(run_class_name):
    return (
        "collisions"
        if determine_is_collisions(run_class_name)
        else "cosmics"
        if determine_is_cosmics(run_class_name)
        else numpy.nan
    )


def determine_has_problem(problem_names, comment, problem_string):
    if type(problem_names) is list and any(
        [problem_string in problem.lower() for problem in problem_names]
    ):
        return True
    # if not pandas.isnull(comment) and problem_string in comment.lower():
    #    return True
    return False


def determine_has_fed_error(problem_names, comment):
    return determine_has_problem(problem_names, comment, "fed error")


def determine_has_dcs_error(problem_names, comment):
    return determine_has_problem(problem_names, comment, "dcs error")


def determine_has_new_hole(problem_names, comment):
    return determine_has_problem(problem_names, comment, "new hole")


def determine_has_dead_channel(problem_names, comment):
    return determine_has_problem(problem_names, comment, "dead channel")


def determine_has_low_signal_noise(problem_names, comment):
    return determine_has_problem(problem_names, comment, "low s/n")


def determine_has_noisy_module(problem_names, comment):
    return determine_has_problem(problem_names, comment, "noisy module")


def determine_has_power_supply_problem(problem_names, comment):
    return determine_has_problem(problem_names, comment, "ps problem")


def determine_has_low_cluster_charge(problem_names, comment):
    return determine_has_problem(problem_names, comment, "low cluster charge")


def determine_has_many_bad_components(problem_names, comment):
    return determine_has_problem(
        problem_names, comment, "large number of bad component"
    )


def determine_has_trigger_problem(problem_names, comment):
    return determine_has_problem(problem_names, comment, "trigger issue")


def determine_is_certification_status_summary(pixel, strip, tracking):
    if all(component == "GOOD" for component in [pixel, strip, tracking]):
        return "Good"

    if all(component == "BAD" for component in [pixel, strip, tracking]):
        return "Bad"

    if all(component == "EXCLUDED" for component in [pixel, strip, tracking]):
        return "Excluded"

    if pixel == "STANDBY" and strip == "STANDBY":
        return "Standby".format(pixel.capitalize())

    if pixel != "GOOD" and strip == "GOOD":
        return "Pixel {}".format(pixel.capitalize())

    if strip != "GOOD" and pixel == "GOOD":
        return "Strip {}".format(strip.capitalize())

    return "Pixel {}, Strip {}".format(pixel.capitalize(), strip.capitalize())


def determine_bad_reason(pixel_comment, strip_comment, tracking_comment, comment):
    possible_reasons = {
        "timing": "timing_scan",
        "config": "misconfiguration",
        "cm threshold": "cm_threshold_scan",
        "hv scan": "hv_scan",
        "hv problem": "hv_problem",
        "hv off": "hv_off",
        "hv is off": "hv_off",
        "stats too low": "low_statistics",
        "on for only": "hv_off",
        "on only": "hv_off",
        "only in": "hv_off",
        "only on": "hv_off",
        "no hv": "hv_off",
        "hv for tracker is off": "hv_off",
        "hv was off": "hv_off",
        "excluded": "excluded",
        "emittance": "emittance_scan",
        "scan": "misc_scan",
        "plots empty": "empty_plots",
        "empty plot": "empty_plots",
        "in daq": "not_in_daq",
        "1 ls": "low_statistics",
        "dqm offline gui": "dqm_gui",
        "low stat": "low_statistics",
    }

    comments = [pixel_comment, strip_comment, tracking_comment, comment]

    for possible_reason_key, possible_reason_value in possible_reasons.items():
        for c in comments:
            if not pandas.isnull(c) and possible_reason_key in c.lower().replace(
                "_", " "
            ):
                return possible_reason_value

    return "miscellaneous"


def determine_online_tracking_status(pixel, strip):
    # TODO dont care about strip for Cosmics runs
    return "BAD" if pixel != "GOOD" or strip != "GOOD" else "GOOD"
