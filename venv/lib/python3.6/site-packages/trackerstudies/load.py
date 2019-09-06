import json
import os

import pandas

from trackerstudies.determine import determine_online_tracking_status
from .exceptions import TrackingMapNotFound
from .merge import merge_runreg_runreg
from .pipes import unify_columns, unify_values

DATA_DIRECTORY = "data"
TRACKING_MAP_DIRECTORY = "TrackEtaPhi_ImpactPoint_GenTk"


def load_tracking_map(run_number, reco):
    file_name = "{}_{}.json".format(run_number, reco.lower())
    path = os.path.join(DATA_DIRECTORY, TRACKING_MAP_DIRECTORY, file_name)
    try:
        with open(path) as file:
            return json.load(file)
    except FileNotFoundError:
        raise TrackingMapNotFound(
            "Unable to load tracking map for run {} ({}). "
            "File '{}' does not exist.".format(run_number, reco, path)
        )


def load_json_as_pandas(file_name):
    """
    :param file_name: output file of runregcrawlr
    :return: pandas dataframe
    """
    with open(file_name) as file:
        return pandas.read_json(file)


def load_run_registry_json(workspace):
    """
    Loads the runregcrawlr-{workspace}-output.json file provided by the runregcrawlr

    :param workspace: workspace name e.g. 'tracker' or 'global'
    :return: pandas dataframe
    """

    filename = "runregcrawlr-{}-output.json".format(workspace)
    path = os.path.join(DATA_DIRECTORY, filename)
    return load_json_as_pandas(path)


def load_tracker_runs():
    return load_run_registry_json("tracker").pipe(unify_columns).pipe(unify_values)


def load_online_tracker_runs():
    """
    Loads Online tracker runs from the global workspaces.

    Discards everything that is not tracker related.
    :return:
    """
    runs = load_run_registry_json("global").pipe(unify_columns).pipe(unify_values)

    runs = runs[runs.reco == "online"]

    runs.loc[:, "tracking"] = runs.apply(
        lambda row: determine_online_tracking_status(row.pixel, row.strip), axis=1
    )

    to_exclude = [
        "dt",
        "l1t",
        "tau_cause",
        "lumi_comment",
        "tau_comment",
        "hlt_cause",
        "muon",
        "cms",
        "hcal_comment",
        "rpc_cause",
        "es_cause",
        "l1tcalo",
        "l1t_comment",
        "dt_cause",
        "csc_comment",
        "lowlumi_cause",
        "ecal_comment",
        "lumi_cause",
        "btag_comment",
        "es",
        "ctpps_comment",
        "jetmet_cause",
        "egamma_cause",
        "hlt_comment",
        "egamma",
        "rpc_comment",
        "ctpps",
        "egamma_comment",
        "l1tcalo_comment",
        "dt_comment",
        "ctpps_cause",
        "l1tmu",
        "tau",
        "cms_comment",
        "run_short",
        "hlt",
        "hcal_cause",
        "hcal",
        "l1t_cause",
        "l1tmu_cause",
        "l1tcalo_cause",
        "cms_cause",
        "run_test",
        "castor_comment",
        "btag",
        "jetmet_comment",
        "muon_cause",
        "rpc",
        "ecal_cause",
        "csc",
        "csc_cause",
        "es_comment",
        "castor_cause",
        "castor",
        "muon_comment",
        "lowlumi",
        "ecal",
        "l1tmu_comment",
        "btag_cause",
        "jetmet",
        "lumi",
        "lowlumi_comment",
    ]

    return runs.drop(to_exclude, axis=1)


def load_global_runs():
    return load_run_registry_json("global").pipe(unify_columns).pipe(unify_values)


def load_all_runreg_runs():
    tracker_runs = load_tracker_runs()
    global_runs = load_global_runs()
    return merge_runreg_runreg(tracker_runs, global_runs)


def load_oms_json(filename):
    path = os.path.join(DATA_DIRECTORY, filename)
    return load_json_as_pandas(path)


def load_oms_runs():
    filename = "oms_runs.json"
    return load_oms_json(filename)


def load_oms_fills():
    filename = "oms_fills.json"
    return load_oms_json(filename)


def load_tkdqmdoctor_runs_json(filename):
    runs = load_json_as_pandas(filename).rename(
        columns={
            "type__reco": "reco",
            "type__beamtype": "beamtype",
            "type__beamenergy": "beamenergy",
            "type__dataset": "dataset",
            "reference_run__reference_run": "reference_run_number",
            "reference_run__reco": "reference_reco",
            "reference_run__runtype": "reference_runtype",
            "reference_run__beamtype": "reference_beamtype",
            "reference_run__beamenergy": "reference_beamenergy",
            "reference_run__dataset": "reference_dataset",
            "data": "certification_date",
        }
    )
    runs.reco = runs.reco.str.lower()
    runs.reference_run_number = runs.reference_run_number.astype(pandas.Int64Dtype())
    return runs


def load_tkdqmdoctor_runs():
    filename = "tkdqmdoctor_runs.json"
    path = os.path.join(DATA_DIRECTORY, filename)
    return load_tkdqmdoctor_runs_json(path)


def load_tkdqmdoctor_problem_runs():
    filename = "tkdqmdoctor_problem_runs.json"
    path = os.path.join(DATA_DIRECTORY, filename)
    return load_tkdqmdoctor_runs_json(path)


def read_histogram_folder(folder_name, attribute_prefix=None):
    folder = os.path.join("data", folder_name)
    file_names = sorted(os.listdir(folder))

    if not attribute_prefix:
        attribute_prefix = folder_name

    attributes = ["rms", "mean", "entries", "integral"]
    attributes = [
        "{}.{}".format(attribute_prefix, attribute) for attribute in attributes
    ]
    columns = ["run_number", "reco", *attributes]

    dataframe = pandas.DataFrame(columns=columns)
    dataframe.set_index(["run_number", "reco"], inplace=True)

    for file_name in file_names:
        run_number, reco = tuple(file_name.replace(".json", "").split("_"))
        run_number = int(run_number)
        path = os.path.join(folder, file_name)
        with open(path) as file:
            histogram = json.load(file)
            rms = histogram["hist"]["stats"]["rms"]["X"]["value"]
            mean = histogram["hist"]["stats"]["mean"]["X"]["value"]
            entries = histogram["hist"]["stats"]["entries"]
            integral = histogram["hist"]["bins"]["integral"]

            dataframe.loc[(run_number, reco), :] = [rms, mean, entries, integral]

    # Convert from dtype object to float for rms, mean, entries and integral
    for attribute in attributes:
        dataframe[attribute] = pandas.to_numeric(dataframe[attribute])

    return dataframe


def load_all_histogram_folders(from_pickle=True):
    """
    This takes a while when doing uncached.
    """

    pickle_path = os.path.join("data", "histograms.pkl")
    try:
        if from_pickle:
            return pandas.read_pickle(pickle_path)
    except FileNotFoundError:
        pass
    prefixes = {
        # Tracking
        "Chi2oNDF_GenTk": "Chi2oNDF",
        "NumberOfRecHitsPerTrack_GenTk": "Hits",
        "NumberOfRecHitsPerTrack_Pixel_GenTk": "Hits.Pixel",
        "NumberOfRecHitsPerTrack_Strip_GenTk": "Hits.Strip",
        "NumberOfSeeds_detachedTripletStepSeeds_detachedTripletStep": "Seeds.detachedTriplet",
        "NumberOfSeeds_initialStepSeeds_initialStep": "Seeds.initialStep",
        "NumberOfSeeds_lowPtTripletStepSeeds_lowPtTripletStep": "Seeds.lowPtTriplet",
        "NumberOfSeeds_mixedTripletStepSeeds_mixedTripletStep": "Seeds.mixedTriplet",
        "NumberOfSeeds_pixelLessStepSeeds_pixelLessStep": "Seeds.pixelLess",
        "NumberOfSeeds_pixelPairStepSeeds_pixelPairStep": "Seeds.pixelPair",
        "NumberOfSeeds_tobTecStepSeeds_tobTecStep": "Seeds.tobTec",
        "NumberOfTracks_GenTk": "Tracks",
        "TrackEta_ImpactPoint_GenTk": "TrackEta",
        "TrackPhi_ImpactPoint_GenTk": "TrackPhi",
        "TrackPt_ImpactPoint_GenTk": "TrackPt",
        # PixelPhase1
        "eventrate_per_BX": "eventrate.BX",
        "deadRocTotal": "deadRoc",
        "num_digis_PXBarrel": "digis.PXBarrel",
        "adc_PXBarrel": "adc.PXBarrel",
        "num_digis_per_LumiBlock_PXBarrel": "digis.lumiblock.PXBarrel",
        "adc_per_LumiBlock_PXBarrel": "adc.lumiblock.PXBarrel",
        "num_digis_PXForward": "digis.PXForward",
        "adc_PXForward": "adc.PXFoward",
        "num_digis_per_LumiBlock_PXForward": "digis.lumiblock.PXForward",
        "adc_per_LumiBlock_PXForward": "adc.lumiblock.PXForward",
        "num_clusters_PXBarrel": "clusters.PXBarrel",
        "num_clusters_PXForward": "clusters.PXForward",
        "num_clusters_per_LumiBlock_PXBarrel": "clusters.lumiblock.PXBarrel",
        "num_clusters_per_LumiBlock_PXForward": "clusters.lumiblock.PXForward",
        "ntracks": "ntracks",
        "ntracksinpixvolume": "ntracksinpixvolume",
        "charge_PXBarrel": "charge.PXBarrel",
        "charge_PXForward": "charge.PXForward",
        "size_PXBarrel": "size.PXBarrel",
        "size_PXForward": "size.PXForward",
        "chargeInner_PXLayer_1": "charge.Inner.PXLayer_1",
        "chargeInner_PXLayer_2": "charge.Inner.PXLayer_2",
        "chargeInner_PXLayer_3": "charge.Inner.PXLayer_3",
        "chargeInner_PXLayer_4": "charge.Inner.PXLayer_4",
        "chargeOuter_PXLayer_1": "charge.Outer.PXLayer_1",
        "chargeOuter_PXLayer_2": "charge.Outer.PXLayer_2",
        "chargeOuter_PXLayer_3": "charge.Outer.PXLayer_3",
        "chargeOuter_PXLayer_4": "charge.Outer.PXLayer_4",
        "charge_PXDisk_+1": "charge.PXDisk_+1",
        "charge_PXDisk_+2": "charge.PXDisk_+2",
        "charge_PXDisk_+3": "charge.PXDisk_+3",
        "charge_PXDisk_-1": "charge.PXDisk_-1",
        "charge_PXDisk_-2": "charge.PXDisk_-2",
        "charge_PXDisk_-3": "charge.PXDisk_-3",
        "residual_x_PXBarrel": "residual.x.PXBarrel",
        "residual_x_PXForward": "residual.x.PXForward",
        "residual_y_PXBarrel": "residual.y.PXBarrel",
        "residual_y_PXForward": "residual.y.PXForward",
        "size_PXLayer_1": "size.PXLayer_1",
        "size_PXLayer_2": "size.PXLayer_2",
        "size_PXLayer_3": "size.PXLayer_3",
        "size_PXLayer_4": "size.PXLayer_4",
        "size_PXDisk_+1": "size.PXDisk_+1",
        "size_PXDisk_+2": "size.PXDisk_+2",
        "size_PXDisk_+3": "size.PXDisk_+3",
        "size_PXDisk_-1": "size.PXDisk_-1",
        "size_PXDisk_-2": "size.PXDisk_-2",
        "size_PXDisk_-3": "size.PXDisk_-3",
        # SiStrip
        "nFEDErrors": "FEDErrors",
        "nBadActiveChannelStatusBits": "BadActiveChannels",
        "Summary_ClusterStoNCorr_OnTrack__TIB": "clusters.OnTrack.TIB",
        "Summary_ClusterStoNCorr_OnTrack__TOB": "clusters.OnTrack.TOB",
        "Summary_ClusterStoNCorr_OnTrack__TID__MINUS": "clusters.OnTrack.TID.MINUS",
        "Summary_ClusterStoNCorr_OnTrack__TID__PLUS": "clusters.OnTrack.TID.PLUS",
        "Summary_ClusterStoNCorr_OnTrack__TEC__MINUS": "clusters.OnTrack.TEC.MINUS",
        "Summary_ClusterStoNCorr_OnTrack__TEC__PLUS": "clusters.OnTrack.TEC.PLUS",
        "Summary_TotalNumberOfClusters_OffTrack__TIB": "clusters.OffTrack.TIB",
        "Summary_TotalNumberOfClusters_OffTrack__TOB": "clusters.OffTrack.TOB",
        "Summary_TotalNumberOfClusters_OffTrack__TID__MINUS": "clusters.OffTrack.TID.MINUS",
        "Summary_TotalNumberOfClusters_OffTrack__TID__PLUS": "clusters.OffTrack.TID.PLUS",
        "Summary_TotalNumberOfClusters_OffTrack__TEC__MINUS": "clusters.OffTrack.TEC.MINUS",
        "Summary_TotalNumberOfClusters_OffTrack__TEC__PLUS": "clusters.OffTrack.TEC.PLUS",
    }

    dataframe = pandas.DataFrame(columns=["run_number", "reco"])
    dataframe.set_index(["run_number", "reco"], inplace=True)

    for folder, prefix in prefixes.items():
        new_dataframe = read_histogram_folder(folder, prefix)
        dataframe = pandas.merge(
            dataframe, new_dataframe, left_index=True, right_index=True, how="outer"
        )

    dataframe.to_pickle(pickle_path)
    return dataframe


def read_histogram_folder_content(folder_name, attribute_prefix=None):
    folder = os.path.join("data", folder_name)
    file_names = sorted(os.listdir(folder))

    if not attribute_prefix:
        attribute_prefix = folder_name

    with open(os.path.join(folder, file_names[0])) as file:
        attribute_length = len(json.load(file)["hist"]["bins"]["content"])

    attributes = [
        "{}_{}".format(attribute_prefix, i) for i in range(0, attribute_length)
    ]

    columns = ["run_number", "reco", *attributes]

    dataframe = pandas.DataFrame(columns=columns)
    dataframe.set_index(["run_number", "reco"], inplace=True)

    # file_names = file_names[1:10]

    for file_name in file_names:
        run_number, reco = tuple(file_name.replace(".json", "").split("_"))
        run_number = int(run_number)
        path = os.path.join(folder, file_name)
        with open(path) as file:
            histogram = json.load(file)
            content = histogram["hist"]["bins"]["content"]
            # print(dataframe)
            # print(len(dataframe.columns))
            # print(len(content))
            dataframe.loc[(run_number, reco), :] = content

    # print(dataframe)
    return dataframe


def load_track_histograms(from_pickle=True):
    pickle_path = os.path.join("data", "track_histogram_contents.pkl")
    try:
        if from_pickle:
            return pandas.read_pickle(pickle_path)
    except FileNotFoundError:
        pass

    folders = {
        "TrackEta_ImpactPoint_GenTk": "TrackEta",
        "TrackPhi_ImpactPoint_GenTk": "TrackPhi",
        "TrackPt_ImpactPoint_GenTk": "TrackPt",
    }

    dataframe = pandas.DataFrame(columns=["run_number", "reco"])
    dataframe.set_index(["run_number", "reco"], inplace=True)

    for folder, prefix in folders.items():
        new_dataframe = read_histogram_folder_content(folder, prefix)
        dataframe = pandas.merge(
            dataframe, new_dataframe, left_index=True, right_index=True, how="outer"
        )

    dataframe.to_pickle(pickle_path)

    return dataframe
