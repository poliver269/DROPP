import numpy as np
from scipy.spatial import distance


def generate_independent_matrix(row, dimension):
    """
    https://stackoverflow.com/questions/61905733/generating-linearly-independent-columns-for-a-matrix
    :param row:
    :param dimension:
    :return:
    """
    matrix = np.random.rand(row, 1)
    rank = 1
    while rank < dimension:
        t = np.random.rand(row, 1)
        if np.linalg.matrix_rank(np.hstack([matrix, t])) > rank:
            matrix = np.hstack([matrix, t])
            rank += 1
    return matrix


def basis_transform(matrix, dimension):
    independent_matrix = generate_independent_matrix(dimension, dimension)
    transformation_matrix = independent_matrix @ np.identity(dimension)
    return np.einsum('tac,cc->tac', matrix, transformation_matrix)


def explained_variance(eigenvalues, component):
    return np.sum(eigenvalues[:component]) / np.sum(eigenvalues)


def gaussian_kern_matrix(size, sig=1.):
    """
    Creates gaussian kernel distribution matrix with the given `size` and a sigma of `sig`.
    https://stackoverflow.com/questions/29731726/how-to-calculate-a-gaussian-kernel-matrix-efficiently-in-numpy
    """
    # lin_array = np.linspace(-(size - 1) / 2., (size - 1) / 2., size)  # linear array (from: -size/2, to: size/2)
    lin_array = np.linspace(0, size, size)  # linear array (from: 0, to: size)
    gauss = np.exp(-0.5 * np.square(lin_array) / np.square(sig))
    kernel = np.outer(gauss, gauss)
    return kernel / np.sum(kernel)


def diagonal_gauss_matrix_kernel(matrix_diagonal_width, sig=1.):
    """
    Gaussian kernel diagonally in the matrix with a specific size and σ (sigma).
    https://peterroelants.github.io/posts/gaussian-process-kernels/
    """
    lin_range = (-1, 1)
    lin_array = np.linspace(*lin_range, matrix_diagonal_width)[:, np.newaxis]  # expand (x,)-array to (x,1)-array
    sq_norm = -0.5 * distance.cdist(lin_array, lin_array, 'sqeuclidean')  # L2 distance (Squared Euclidian)
    return np.exp(sq_norm / np.square(sig))  # gaussian


def is_matrix_symmetric(matrix, rtol=1e-05, atol=1e-08):
    """
    Checks a matrix for its symmetric behavior.
    https://stackoverflow.com/questions/42908334/checking-if-a-matrix-is-symmetric-in-numpy
    :param matrix: array_like
    :param rtol: float
        The relative tolerance parameter.
    :param atol: float
        The absolute tolerance parameter.
    :return: bool
        Returns True if the matrix is symmetric within a tolerance.
    """
    return np.allclose(matrix, matrix.T, rtol=rtol, atol=atol)


def is_matrix_orthogonal(matrix, rtol=1e-05, atol=1e-08):
    """
    Checks if the rows of the given matrix are orthogonal:
    https://stackoverflow.com/a/62587115/11566305
    :param matrix: array_like
    :param rtol: float
        The relative tolerance parameter
    :param atol: float
        The absolute tolerance parameter
    :return: bool
        Returns True if the matrix rows are orthogonal within a tolerance.
    """
    return np.allclose(matrix.T @ matrix, np.eye(matrix.shape[1]), rtol=rtol, atol=atol)


def exponential_2d(x, sigma):
    """
    Function from:
    https://medium.com/geekculture/kernel-methods-in-support-vector-machines-bb9409342c49
    :param x: int or ndarray
    :param sigma:
    :return:
    """
    return np.exp(-np.abs(x) / (2 * np.power(sigma, 2.)))


def epanechnikov_2d(x, sigma):
    return 1 - (np.power(x, 2.) / np.power(sigma, 2.))


def gaussian_2d(x, mu, sigma):
    return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sigma, 2.)))


def my_sinc(x, sigma):
    return np.sinc((x * sigma * np.pi) / len(x))


def my_sinc_sum(x, mu, sigma):
    return mu + np.sinc(x * sigma)


def my_cos(x, sigma):
    return np.cos((4 * sigma * np.pi * x) / len(x))
