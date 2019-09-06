from .determine import (
    determine_runtype,
    determine_tracker_is_bad,
    determine_is_heavy_ion,
    determine_is_commissioning,
    determine_is_special,
    determine_has_fed_error,
    determine_has_dcs_error,
    determine_has_new_hole,
    determine_has_dead_channel,
    determine_has_low_signal_noise,
    determine_has_noisy_module,
    determine_has_power_supply_problem,
    determine_has_low_cluster_charge,
    determine_has_many_bad_components,
    determine_has_trigger_problem,
    determine_is_certification_status_summary,
    determine_bad_reason,
)


def _unify_column_names(column_names):
    new_names = []
    for c in column_names:
        if c.endswith("rda_cmp_pix") or c.startswith("rda_cmp_pix_"):
            new_names.append(c.replace("pix", "pixel"))
        elif c.endswith("rda_cmp_track") or c.startswith("rda_cmp_track_"):
            new_names.append(c.replace("track", "tracking"))
        elif c == "rda_wor_name":
            new_names.append("workspace")
        else:
            new_names.append(c)
    return new_names


def _remove_prefix(items, prefix):
    return [item.replace(prefix, "") for item in items]


def unify_columns(data_frame):
    column_names = list(data_frame)
    new_names = _unify_column_names(column_names)
    new_names = _remove_prefix(new_names, "rda_cmp_")
    data_frame.columns = new_names
    return data_frame


def unify_values(dataframe):
    dataframe.reco = dataframe.reco.str.lower()
    dataframe.workspace = dataframe.workspace.str.lower()
    dataframe["reco"] = dataframe["reco"].replace(regex="promptreco", value="prompt")
    return dataframe


def add_runtype(dataframe):
    # Handle obvious cases
    dataframe["runtype"] = dataframe.apply(
        lambda row: determine_runtype(row.run_class_name), axis=1
    )

    return dataframe


def add_is_bad(df):
    if "runtype" not in df:
        add_runtype(df)
    df.loc[:, "is_bad"] = df.apply(
        lambda row: determine_tracker_is_bad(
            row.pixel, row.strip, row.tracking, row.runtype
        ),
        axis=1,
    )
    return df


def add_reference_cost(dataframe):
    from .utils import calculate_tracking_map_reference_cost

    dataframe.loc[:, "reference_cost"] = dataframe.apply(
        lambda row: calculate_tracking_map_reference_cost(
            row.run_number, row.reference_run_number, row.reco
        ),
        axis=1,
    )
    return dataframe


def add_angular_entropy(dataframe):
    from trackerstudies.utils import (
        get_entropy_cache,
        save_entropy_cache,
        get_angular_entropy,
    )

    entropy_cache = get_entropy_cache()

    dataframe.loc[:, "angular_entropy"] = dataframe.apply(
        lambda row: get_angular_entropy(row.run_number, row.reco, entropy_cache), axis=1
    )

    save_entropy_cache(entropy_cache)
    return dataframe


def add_is_reference_run(dataframe):
    raise NotImplementedError


def add_is_heavy_ion(dataframe):
    dataframe.loc[:, "is_heavy_ion"] = dataframe.apply(
        lambda row: determine_is_heavy_ion(row.rda_name), axis=1
    )
    return dataframe


def add_is_commissioning(dataframe):
    dataframe.loc[:, "is_commissioning"] = dataframe.apply(
        lambda row: determine_is_commissioning(row.run_class_name, row.rda_name), axis=1
    )

    dataframe.loc[
        dataframe.run_number.isin(
            dataframe[dataframe["is_commissioning"]].run_number.unique()
        ),
        "is_commissioning",
    ] = True
    return dataframe


def add_is_special(dataframe):
    dataframe.loc[:, "is_special"] = dataframe.apply(
        lambda row: determine_is_special(row.run_class_name, row.rda_name), axis=1
    )
    return dataframe


def extract_run_numbers(dataframe):
    """
    :param dataframe: pandas dataframe containing the runs
    :return: list of unique run numbers
    """
    return list(dataframe.run_number.unique())


def add_problem_column(dataframe, new_column_name, determine_function):
    dataframe.loc[:, new_column_name] = dataframe.apply(
        lambda row: determine_function(row.problem_names, row.comment), axis=1
    )

    problem_run_numbers = extract_run_numbers(dataframe[dataframe[new_column_name]])
    dataframe.loc[
        dataframe.run_number.isin(problem_run_numbers), new_column_name
    ] = True
    return dataframe


def add_all_problems(dataframe):
    return (
        dataframe.pipe(add_problem_column, "has_fed_error", determine_has_fed_error)
        .pipe(add_problem_column, "has_dcs_error", determine_has_dcs_error)
        .pipe(add_problem_column, "has_new_hole", determine_has_new_hole)
        .pipe(add_problem_column, "has_dead_channel", determine_has_dead_channel)
        .pipe(
            add_problem_column, "has_low_signal_noise", determine_has_low_signal_noise
        )
        .pipe(add_problem_column, "has_noisy_module", determine_has_noisy_module)
        .pipe(add_problem_column, "has_ps_problem", determine_has_power_supply_problem)
        .pipe(
            add_problem_column,
            "has_low_cluster_charge",
            determine_has_low_cluster_charge,
        )
        .pipe(
            add_problem_column,
            "has_many_bad_components",
            determine_has_many_bad_components,
        )
        .pipe(add_problem_column, "has_trigger_problem", determine_has_trigger_problem)
    )


def add_status_summary(dataframe):
    """
    Certification status summary

    - "Good"
    - "Pixel Bad"
    - "Strip Bad"
    - "Tracking Bad"
    - "Pixel Excluded, Tracking Bad"
    ...
    - "Bad"
    """
    dataframe.loc[:, "status_summary"] = dataframe.apply(
        lambda row: determine_is_certification_status_summary(
            row.pixel, row.strip, row.tracking
        ),
        axis=1,
    )
    return dataframe


def add_bad_reason(dataframe):
    dataframe.loc[dataframe.tracking == "BAD", "bad_reason"] = dataframe.apply(
        lambda row: determine_bad_reason(
            row.pixel_comment, row.strip_comment, row.tracking_comment, row.comment
        ),
        axis=1,
    )
    return dataframe
