import numpy


def extract_tracking_map_content(tracking_map):
    return numpy.array(tracking_map["hist"]["bins"]["content"])


def extract_tracking_map_labels(tracking_map):
    xlabel = tracking_map["hist"]["xaxis"]["title"]
    ylabel = tracking_map["hist"]["yaxis"]["title"]
    return xlabel, ylabel


def extract_tracking_map_title(tracking_map):
    return tracking_map["hist"]["title"]
