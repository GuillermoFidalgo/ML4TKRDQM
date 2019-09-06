import math

import numpy as np
from scipy import stats


def distance(x1, y1, x2, y2):
    # note to self: add phi continuity
    delta_x = x2 - x1
    delta_y = y2 - y1
    return math.sqrt(delta_x ** 2 + delta_y ** 2)


def angular_correlation(matrix):
    # TODO check http://www.astroml.org/user_guide/correlation_functions.html
    # TODO use numpy mathematics

    angular_distances = []
    correlations = []

    for x1 in range(0, np.shape(matrix)[0]):
        for y1 in range(0, np.shape(matrix)[1]):
            for x2 in range(0, np.shape(matrix)[0]):
                for y2 in range(0, np.shape(matrix)[1]):
                    angular_distances.append(distance(x1, y1, x2, y2))
                    correlations.append(math.fabs(matrix[x1][y1] - matrix[x2][y2]))

    return angular_distances, correlations


def binned_angular_correlation(matrix):
    angular_distances, correlations = angular_correlation(matrix)

    bin_means, bin_edges, bin_number = stats.binned_statistic(
        angular_distances, correlations, statistic="mean", bins=50
    )
    bin_width = bin_edges[1] - bin_edges[0]
    bin_centers = bin_edges[1:] - bin_width / 2

    return bin_centers, bin_means


def angular_correlation_entropy(matrix):
    bins, correlations = binned_angular_correlation(matrix)
    return entropy(correlations)


def entropy(data):
    return stats.entropy(data)


def scaled_reference_cost(matrix, reference_matrix):
    scale_factor = most_common_scale(matrix, reference_matrix)
    if np.isnan(scale_factor):
        return np.inf

    matrix_scaled = matrix * scale_factor

    reference_mean = reference_matrix.mean()
    reference_std = reference_matrix.std()

    matrix_normalized = np.divide(
        np.subtract(matrix_scaled, reference_mean), reference_std
    )
    reference_normalized = np.divide(
        np.subtract(reference_matrix, reference_mean), reference_std
    )

    return mean_squared_error(matrix_normalized, reference_normalized)


def reference_cost(matrix, reference_matrix):
    if not np.any(matrix) or not np.any(reference_matrix):
        return np.inf
    matrix_normalized = mean_normalize(matrix)
    reference_matrix_normalized = mean_normalize(reference_matrix)
    try:
        return mean_squared_error(matrix_normalized, reference_matrix_normalized)
    except ValueError:
        # Incompatible matrices
        return np.nan


def mean_normalize(data):
    # TODO
    #  RuntimeWarning: invalid value encountered in true_divide
    #  RuntimeWarning: invalid value encountered in greater_equal
    #       keep = (tmp_a >= first_edge)
    #  RuntimeWarning: invalid value encountered in less_equal
    #       keep &= (tmp_a <= last_edge)

    mean = np.mean(data)
    standard_deviation = np.std(data)
    return np.divide(np.subtract(data, mean), standard_deviation)


def mean_squared_error(x, y):
    return ((x - y) ** 2).mean() / 2


def most_common_scale(matrix, reference_matrix):
    """
    :return: most common scale factor to scale matrix to reference_matrix
    """
    try:
        ratios = np.divide(reference_matrix, matrix)
    except ValueError:
        # TODO ValueError: operands could not be broadcast together with shapes (32,31) (32,26)
        return np.nan
    ratios_vector = np.reshape(ratios, ratios.size)
    ratios_vector = ratios_vector[(ratios_vector < np.inf) & (ratios_vector > np.NINF)]
    if ratios_vector.size == 0:
        return np.nan

    # Put all elements in bins
    hist, bin_edges = np.histogram(ratios_vector)

    # Choose bin with biggest count
    biggest_bin_index = np.argmax(hist)

    lower_border = bin_edges[biggest_bin_index]
    upper_border = bin_edges[biggest_bin_index + 1]

    if biggest_bin_index + 1 == len(hist):
        upper_border += 1

    values = ratios_vector[
        (ratios_vector >= lower_border) & (ratios_vector < upper_border)
    ]

    return np.median(values)
