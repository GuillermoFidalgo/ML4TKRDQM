import os

import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

from trackerstudies.utils import load_tracking_map_content, setup_pandas_display
from .algorithms import binned_angular_correlation, most_common_scale
from .extract import (
    extract_tracking_map_content,
    extract_tracking_map_labels,
    extract_tracking_map_title,
)
from .load import load_tracking_map
from .plotutils import (
    plot_matrix,
    plot_line,
    save_with_default_name,
    plot_histogram,
    plot_3d_matrix,
    _post_process_plot,
)

from matplotlib import cm
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D


def plot_tracking_map(run_number, reco, *args, **kwargs):
    tracking_map = load_tracking_map(run_number, reco)
    matrix = extract_tracking_map_content(tracking_map)
    xlabel, ylabel = extract_tracking_map_labels(tracking_map)
    title = "{}\n{} ({})".format(
        extract_tracking_map_title(tracking_map), run_number, reco
    )

    if kwargs.get("save", False) is True:
        kwargs["save"] = "tracking_map_{}_{}.pdf".format(run_number, reco)

    plot_matrix(matrix, xlabel=xlabel, ylabel=ylabel, title=title, *args, **kwargs)


def plot_tracking_map_3d(run_number, reco, *args, **kwargs):
    tracking_map = load_tracking_map(run_number, reco)
    matrix = extract_tracking_map_content(tracking_map)
    xlabel, ylabel = extract_tracking_map_labels(tracking_map)
    title = "{}\n{} ({})".format(
        extract_tracking_map_title(tracking_map), run_number, reco
    )

    if kwargs.get("save", False) is True:
        kwargs["save"] = "tracking_map_3d_{}_{}.pdf".format(run_number, reco)

    plot_3d_matrix(matrix, xlabel=xlabel, ylabel=ylabel, title=title, *args, **kwargs)


def plot_tracking_map_line(run_number, reco, *args, **kwargs):
    tracking_map = load_tracking_map(run_number, reco)
    matrix = extract_tracking_map_content(tracking_map)
    xlabel, ylabel = extract_tracking_map_labels(tracking_map)
    title = "{}\n{} ({})".format(
        extract_tracking_map_title(tracking_map), run_number, reco
    )

    matrix = np.transpose(matrix)
    y = np.reshape(matrix, matrix.size)
    x = np.arange(0, matrix.size)

    if kwargs.get("save", False) is True:
        kwargs["save"] = "tracking_map_line_{}_{}.pdf".format(run_number, reco)

    plot_line(x, y, xlabel=xlabel, ylabel=ylabel, title=title, *args, **kwargs)


def plot_tracking_maps_line_vs_reference(
    run_number, reference_run_number, reco, *args, **kwargs
):
    tracking_map = load_tracking_map(run_number, reco)
    tracking_map_content = extract_tracking_map_content(tracking_map)
    reference_map_content = load_tracking_map_content(reference_run_number, reco)

    scale = most_common_scale(tracking_map_content, reference_map_content)
    tracking_map_scaled = tracking_map_content * scale

    max = np.max(reference_map_content)

    tracking_map_normalized = tracking_map_scaled / max
    refrence_map_normalized = reference_map_content / max

    fig, ax = plt.subplots()

    matrix = np.transpose(tracking_map_normalized)
    y = np.reshape(matrix, matrix.size)
    x = np.arange(0, matrix.size)

    matrix_ref = np.transpose(refrence_map_normalized)
    y_ref = np.reshape(matrix_ref, matrix_ref.size)
    x_ref = np.arange(0, matrix_ref.size)

    plt.plot(x, y, alpha=0.75, label=run_number)
    plt.plot(x_ref, y_ref, alpha=0.75, label=reference_run_number)

    plt.legend()
    vals = ax.get_yticks()
    ax.set_yticklabels(["{:,.2%}".format(x) for x in vals])

    xlabel, ylabel = extract_tracking_map_labels(tracking_map)
    title = "{}\n{} (scaled) vs. {} ({})".format(
        extract_tracking_map_title(tracking_map), run_number, reference_run_number, reco
    )

    if kwargs.get("title", None):
        title = "{}\n{}".format(title, kwargs.pop("title"))

    _post_process_plot(xlabel=xlabel, ylabel=ylabel, title=title, *args, **kwargs)


def plot_multiple_tracking_maps_line(run_numbers, reco, *args, **kwargs):
    fig, ax = plt.subplots()

    for run_number in run_numbers:
        tracking_map = load_tracking_map_content(run_number, reco)
        matrix = np.transpose(tracking_map)
        y = np.reshape(matrix, matrix.size)
        x = np.arange(0, matrix.size)
        plt.plot(x, y, label=run_number)

    plt.legend()
    if kwargs.get("save", False) is True:
        kwargs["save"] = "tracking_map_line_{}_{}.pdf".format(run_number, reco)
    _post_process_plot(*args, **kwargs)


def plot_multiple_tracking_maps_line_scaled(run_numbers, reco, *args, **kwargs):
    fig, ax = plt.subplots()

    for run_number in run_numbers:
        tracking_map = load_tracking_map_content(run_number, reco)
        matrix = np.transpose(tracking_map)
        y = np.reshape(matrix, matrix.size)
        x = np.arange(0, matrix.size)
        plt.plot(x, y, label=run_number)

    plt.legend()
    if kwargs.get("save", False) is True:
        kwargs["save"] = "tracking_map_line_{}_{}.pdf".format(run_number, reco)
    _post_process_plot(*args, **kwargs)


def plot_reference_distribution(dataframe, *args, **kwargs):
    g = sns.FacetGrid(dataframe, col="reco", row="runtype", hue="is_bad")
    g.map(plt.scatter, "run_number", "reference_run_number", alpha=0.7)

    save_with_default_name(kwargs.get("save", False), "reference_distribution.pdf")

    if kwargs.get("show", False):
        plt.show()


def plot_pairs(dataframe, columns=None, *args, **kwargs):
    columns = (
        columns
        if columns
        else ["run_number", "lhc_fill", "lumisections", "run_lumi", "run_live_lumi"]
    )

    sns.pairplot(dataframe[columns])

    save_with_default_name(kwargs.get("save", False), "pair_plot.pdf")

    if kwargs.get("show", False):
        plt.show()


def plot_angular_correlation(run_number, reco, *args, **kwargs):
    tracking_map = load_tracking_map(run_number, reco)
    matrix = extract_tracking_map_content(tracking_map)
    bins, correlation = binned_angular_correlation(matrix)

    xlabel = "Binned Two Point Distance"
    ylabel = "Average Delta Occupancy"
    title = "Angular correlation {} ({})".format(run_number, reco)

    if kwargs.get("save", False) is True:
        kwargs["save"] = "angular_correlation_{}_{}.pdf".format(run_number, reco)

    plot_line(
        bins, correlation, xlabel=xlabel, ylabel=ylabel, title=title, *args, **kwargs
    )


def plot_reference_cost(dataframe, *args, **kwargs):
    g = sns.FacetGrid(dataframe, col="reco", row="runtype", hue="is_bad")
    g = g.map(plt.scatter, "run_number", "reference_cost", alpha=0.7)

    save_with_default_name(kwargs.get("save", False), "reference_cost.pdf")

    if kwargs.get("show", False):
        plt.show()


def plot_angular_entropy(dataframe, *args, **kwargs):
    g = sns.FacetGrid(dataframe, col="reco", row="runtype", hue="is_bad")
    g.map(plt.scatter, "run_number", "angular_entropy", alpha=0.7)

    path = os.path.join("plots", "angular_entropy.pdf")
    save_with_default_name(kwargs.get("save", False), path)

    if kwargs.get("show", False):
        plt.show()


def plot_referenced_tracking_map_histogram(
    run_number, reference_run_number, reco, *args, **kwargs
):
    tk_map = load_tracking_map_content(run_number, reco)
    reference_map = load_tracking_map_content(reference_run_number, reco)
    ratios = np.divide(tk_map, reference_map)
    title = "{} vs {} ({})".format(run_number, reference_run_number, reco)
    if kwargs.get("title", None):
        title = "{}\n{}".format(title, kwargs.pop("title"))

    plot_histogram(ratios, title=title, *args, **kwargs)


def plot_reference_subtracted_tracking_map(
    run_number, reference_run_number, reco, *args, **kwargs
):
    tracking_map = load_tracking_map(run_number, reco)
    tracking_map_content = extract_tracking_map_content(tracking_map)
    reference_map_content = load_tracking_map_content(reference_run_number, reco)
    scale = most_common_scale(tracking_map_content, reference_map_content)
    tracking_map_scaled = tracking_map_content * scale
    max = np.max(reference_map_content)

    tracking_map_normalized = tracking_map_scaled / max
    refrence_map_normalized = reference_map_content / max

    xlabel, ylabel = extract_tracking_map_labels(tracking_map)
    title = "Subtracted {}\n{} - {} (scaled) ({})".format(
        extract_tracking_map_title(tracking_map), reference_run_number, run_number, reco
    )

    if kwargs.get("title", None):
        title = "{}\n{}".format(title, kwargs.pop("title"))

    plot_matrix(
        refrence_map_normalized - tracking_map_normalized,
        xlabel=xlabel,
        ylabel=ylabel,
        title=title,
        *args,
        **kwargs
    )


def plot_reference_subtracted_tracking_map_3d(
    run_number, reference_run_number, reco, *args, **kwargs
):
    tracking_map = load_tracking_map(run_number, reco)
    xlabel, ylabel = extract_tracking_map_labels(tracking_map)
    matrix = extract_tracking_map_content(tracking_map)

    reference_map = load_tracking_map_content(reference_run_number, reco)
    scale = most_common_scale(matrix, reference_map)
    tracking_map_scaled = matrix * scale
    max = np.max(reference_map)

    tracking_map_normalized = tracking_map_scaled / max
    refrence_map_normalized = reference_map / max

    scale_factor = np.around(scale, decimals=1)

    title = "{}\n{} - {} (scaled * {}) ({})".format(
        extract_tracking_map_title(tracking_map),
        reference_run_number,
        run_number,
        scale_factor,
        reco,
    )

    if kwargs.get("title", None):
        title = "{}\n{}".format(title, kwargs.pop("title"))

    try:
        matrix = refrence_map_normalized - tracking_map_normalized
    except ValueError:
        # TODO ValueError: operands could not be broadcast together with shapes (32,31) (32,26)
        return

    if not kwargs.get("vmin", None):
        max = np.max(matrix)
        min = np.min(matrix)
        maximum = np.maximum(np.abs(max), np.abs(min))
        kwargs["vmax"] = maximum
        kwargs["vmin"] = -maximum

    plot_3d_matrix(
        matrix,
        xlabel=xlabel,
        ylabel=ylabel,
        title=title,
        use_percent=True,
        *args,
        **kwargs
    )


def plot_tracking_maps_side_by_side(
    run_number,
    reference_run_number,
    reco,
    is_bad=None,
    subtitle=None,
    subdir=None,
    show=False,
):
    tracking_map = load_tracking_map(run_number, reco)

    tracking_map_content = extract_tracking_map_content(tracking_map)
    reference_map_content = load_tracking_map_content(reference_run_number, reco)

    map_title = extract_tracking_map_title(tracking_map)
    xlabel, ylabel = extract_tracking_map_labels(tracking_map)

    fig, ax = plt.subplots(1, 3, figsize=(8, 4.5))

    ax[0].imshow(tracking_map_content)
    title = "{}".format(run_number)
    if is_bad is not None:
        title += " (Bad)" if is_bad else " (Good)"
    ax[0].set_title(title)

    ax[2].imshow(reference_map_content)
    title = "{} (ref)".format(reference_run_number)
    ax[2].set_title(title)

    scale = most_common_scale(tracking_map_content, reference_map_content)
    tracking_map_scaled = tracking_map_content * scale
    max = np.max(reference_map_content)

    tracking_map_normalized = tracking_map_scaled / max
    refrence_map_normalized = reference_map_content / max

    try:
        matrix = refrence_map_normalized - tracking_map_normalized

        max = np.max(matrix)
        min = np.min(matrix)
        maximum = np.maximum(np.abs(max), np.abs(min))
        vmax = maximum
        vmin = -maximum

        scale_factor = np.around(scale, decimals=1)

        ax[1].imshow(matrix, vmax=vmax, vmin=vmin, cmap=cm.seismic)
        title = "{} - {} \n Scale: {}".format(
            reference_run_number, run_number, scale_factor
        )
        ax[1].set_title(title)
    except ValueError as e:
        # TODO ValueError: operands could not be broadcast together with shapes (32,31) (32,26)
        print(e)

    suptitle = "{} ({})".format(map_title, reco)
    if subtitle:
        suptitle = "{}\n{}".format(suptitle, subtitle)

    fig.suptitle(suptitle)

    directory = "plots/tracking_map_side_by_side"
    if subdir:
        directory = os.path.join(directory, subdir)
    file_name = "{}_vs_{}_{}.png".format(run_number, reference_run_number, reco)

    if not os.path.exists(directory):
        os.makedirs(directory)

    path = os.path.join(directory, file_name)

    plt.savefig(path)
    if show:
        plt.show()


def plot_luminosity_by_lumisections(dataframe, *args, **kwargs):
    g = sns.FacetGrid(dataframe, col="reco", row="runtype", hue="is_bad")
    g.map(plt.scatter, "run_number", "reference_run_number", alpha=0.7)

    save_with_default_name(kwargs.get("save", False), "reference_distribution.pdf")

    if kwargs.get("show", False):
        plt.show()


def plot_luminosity_lumisection_ratio(dataframe, *args, **kwargs):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    cmap = cm.get_cmap("viridis")
    ax.scatter(
        dataframe.run_number,
        dataframe.lumisections,
        dataframe.recorded_lumi,
        c=dataframe.is_bad,
        cmap=cmap,
        s=60,
    )
    ax.set(xlabel="Run Number", ylabel="Lumisections", zlabel="Recorded Luminosity")
    # ax.view_init(45, 0)
    plt.show()


def plot_histogram_pairs(dataframe, *args, **kwargs):
    import seaborn as sns

    sns.set(style="ticks", color_codes=True)
    iris = sns.load_dataset("iris")
    g = sns.pairplot(iris, hue="species", palette="husl")
    print()
    print(iris)
    plt.show()

    histograms = ["Hits", "Hits.Pixel", "Hits.Strip"]
    rms = ["{}.rms".format(h) for h in histograms]
    df = dataframe[[*rms, "run_number"]]

    setup_pandas_display()

    df = df[df["Hits.rms"] > 0]
    df = df[df["Hits.Pixel.rms"] > 0]
    df = df[df["Hits.Strip.rms"] > 0]
    print(df)
    print(sorted(list(df["Hits.rms"].unique())))
    print(sorted(list(df["Hits.Pixel.rms"].unique())))
    print(sorted(list(df["Hits.Strip.rms"].unique())))
    g = sns.pairplot(df)
    plt.show()
    """"
    #histograms = ['Chi2oNDF', 'Hits', 'Hits.Pixel', 'Hits.Strip', 'Seeds.detachedTriplet', 'Seeds.initialStep', 'Seeds.lowPtTriplet', 'Seeds.mixedTriplet', 'Seeds.pixelLess', 'Seeds.pixelPair', 'Seeds.tobTec', 'Tracks', 'TrackEta', 'TrackPhi', 'TrackPt']
    histograms = ['Hits', 'Hits.Pixel', 'Hits.Strip']

    rms = ["{}.rms".format(h) for h in histograms]
    mean = ["{}.rms".format(h) for h in histograms]
    integral = ["{}.rms".format(h) for h in histograms]
    entries = ["{}.rms".format(h) for h in histograms]
    df = dataframe[[*mean]]
    print()
    setup_pandas_display()
    df = df.tail()
    print(df)
    plt.plot(df["Hits.rms"], df['Hits.Pixel.rms'])
    #sns.pairplot(df)
    plt.show()
    """
