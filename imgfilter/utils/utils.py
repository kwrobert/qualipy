"""
Common utilities used in the library.
"""

import numpy


# Numba integration
# If Numba is installed, certain functions are automatically
# sped-run by Numba's JIT compilation.
try:
    import numba
    jit = numba.jit

except ImportError:

    def jit(func):
        return func


def partition_matrix(matrix, n):
    """Partitions a matrix into n x n blocks of equal size

    :param matrix: the matrix to partition
    :type matrix: numpy.ndarray
    :param n: the size of the side of one partition
    :type n: int
    :returns: numpy.ndarray
    """
    height, width = matrix.shape
    y_stride, x_stride = height / n, width / n

    partitions = [matrix]
    for y in xrange(0, y_stride * n, y_stride):
        for x in xrange(0, x_stride * n, x_stride):
            partitions.append(matrix[y : y + y_stride,
                                     x : x + x_stride])

    return partitions


def normalize(arr):
    """Normalizes an array of values to the range [0, 1]

    :param arr: the array to normalize
    :type arr: numpy.ndarray
    :returns: numpy.ndarray
    """
    arr_min, arr_max = numpy.min(arr), numpy.max(arr)

    if arr_min == arr_max:
        return numpy.ones(len(arr))

    return (arr - arr_min) / (arr_max - arr_min)


def flatten(lists):
    """Flattens a list of lists into a single list

    :param lists: the list of lists to flatten
    :type lists: list
    :returns: list
    """
    return [item for sublist in lists for item in sublist]

def clipping_percentage(histogram, threshold, overThreshold):
	"""Calculates percentage of images high of low intensity pixels
	
	:param histogram: intensity histogram
	:type histogram: 8 bit histogram
	:param threshold: threshold intensity which is used to get intensity amounts over or under it
	:type threshold: integer value in range of 0 to 255
	:param overThreshold: whether to get intensity amount over(True) or under(False) threshold
	:type boolean
	:returns: float
	""" 
	
	total = numpy.sum(histogram)
	if total < 0.0005:  # avoid division by zero
		return 0
	if overThreshold:
		return float(numpy.sum(histogram[threshold:])) / total
	else:
		return float(numpy.sum(histogram[:threshold])) / total
