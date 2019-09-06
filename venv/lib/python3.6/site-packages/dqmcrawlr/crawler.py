from dqmcrawlr import jsonfairy
from dqmcrawlr.dqm import DQMSession


def _get_tracking_map_resource_name(reconstruction):
    plot = "TrackEtaPhi_ImpactPoint_GenTk"

    path = "/Tracking/TrackParameters/"
    if reconstruction.lower() != "online":
        path += "generalTracks/"
    path += "GeneralProperties/"

    return path + plot


class DQMCrawler:
    def __init__(self, dataset_cache=None):
        self.dqm_session = DQMSession()
        if dataset_cache:
            self.dqm_session.cache.datasets.update(dataset_cache)

    def get_json(self, run_number, reconstruction, resource):
        """
        :param resource: Name of the resource, e.g. "/Tracking/TrackParameters/generalTracks/GeneralProperties/TrackEtaPhi_ImpactPoint_GenTk"
        :param run_number: Run number, e.g. 321233
        :param reconstruction: Reconstruction type, e.g. "Prompt", "Express" or even "Online"
        :return:
        """
        reconstruction = reconstruction.lower()

        if reconstruction == "online":
            dataset = "/Global/Online/ALL"
            service = "online"
        else:
            dataset = self.dqm_session.get_dataset(run_number, reconstruction)
            service = "offline"

        return jsonfairy.get_json(run_number, dataset, resource, service)

    def get_tracking_map(self, run_number, reconstruction):
        """
        Tries to retrieve the resource TrackEtaPhi_ImpactPoint_GenTk.

        Works for collisions runs only.

        :param run_number: Run number
        :param reconstruction: "Express", "Prompt", "reReco" or "Online"
        :return:
        """
        resource = _get_tracking_map_resource_name(reconstruction)
        return self.get_json(run_number, reconstruction, resource)
