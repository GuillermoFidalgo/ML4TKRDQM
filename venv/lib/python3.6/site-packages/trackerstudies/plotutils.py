import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm

# noinspection PyUnresolvedReferences
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import


def plot_matrix(matrix, *args, **kwargs):
    fig, ax = plt.subplots()
    plt.imshow(matrix)
    _post_process_plot(*args, **kwargs)


def plot_3d_matrix(matrix, use_percent=False, *args, **kwargs):
    fig = plt.figure()
    ax = fig.gca(projection="3d")

    Z = np.array(matrix)
    line_count, column_count = Z.shape

    X = np.arange(0, column_count, 1)
    Y = np.arange(0, line_count, 1)
    X, Y = np.meshgrid(X, Y)

    surf = ax.plot_surface(
        X,
        Y,
        Z,
        cmap=cm.coolwarm,
        vmin=kwargs.pop("vmin", None),
        vmax=kwargs.pop("vmax", None),
        linewidth=0,
        antialiased=False,
    )

    fig.colorbar(surf, shrink=0.5, aspect=5)
    ax.view_init(kwargs.pop("elev", None), kwargs.pop("azim", None))

    if use_percent:
        vals = ax.get_zticks()
        ax.set_zticklabels(["{:,.2%}".format(x) for x in vals])
    _post_process_plot(*args, **kwargs)


def plot_line(x, y, *args, **kwargs):
    fig, ax = plt.subplots()
    plt.plot(x, y)
    _post_process_plot(*args, **kwargs)


def plot_histogram(x, bins=10, *args, **kwargs):
    fig, ax = plt.subplots()
    plt.hist(x, bins, facecolor="blue")
    _post_process_plot(*args, **kwargs)


def _post_process_plot(title=None, xlabel=None, ylabel=None, show=False, save=None):
    if title:
        plt.title(title)
    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)
    if save:
        file_name = save
        save_plot(file_name)
    if show:
        plt.show()


def save_plot(file_name):
    plt.savefig(file_name)


def save_with_default_name(save, default):
    if save:
        if save is True:
            file_name = default
        else:
            file_name = save
        save_plot(file_name)
