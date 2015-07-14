"""
Filter for detecting pattern-like images.

The image is first turned into grayscale, after which discrete
fast fourier transformation is applied to construct the magnitude
spectrum of the image. Then frequencies which have intermediate
or low intensities are removed from the magnitude spectrum and
all frequencies with high intensity are intensified to the max
value. After this the distance from the center for each high
intensity frequency is calculated. From this set of distances
anomalies are removed by using the local outlier factor method.

The max from the set of distances is taken. This max distance is
then used as a radius for a circle, and all points outside this
circle in the magnitude spectrum are excluded and the density of
high frequencies is calculated. This density is used to estimate
how pattern-like the image is. Pattern-like images usually exhibit
smaller density than non-pattern-like images.
"""

import cv2
import numpy

from ..analyzers.common.statistic_common import *
from ..analyzers.magnitude_spectrum import count_magnitude_spectrum

from filter import Filter


def distances_from_center(height, width):
    """Returns a matrix of distances from each element to the center of
    a matrix of certain size.

    :param height: height of the matrix
    :type height: int
    :param width: width of the matrix
    :type width: int
    :returns: numpy.ndarray -- the distance matrix
    """
    yy, xx = numpy.mgrid[:height, :width]
    return (xx - width / 2.0) ** 2 + (yy - height / 2.0) ** 2


def pattern_recognition(magnitude_spectrum):
    """Returns a prediction of how pattern-like an image is

    :param magnitude_spectrum: magnitude spectrum of a two-color image
    :type magnitude_spectrum: numpy.ndarray
    :returns: float
    """
    circle = distances_from_center(*magnitude_spectrum.shape)

    mask = magnitude_spectrum > 0.7
    all_distances = numpy.sqrt(circle[mask].flatten())

    all_distances = remove_anomalies(all_distances, 0.4)
    max_distances = get_max_values(all_distances, 20)
    max_distance_avg = numpy.mean(max_distances)

    donut = circle >= max_distance_avg ** 2
    intense_points = numpy.sum(mask & numpy.logical_not(donut))
    all_points = magnitude_spectrum.size - numpy.sum(donut)

    return intense_points / float(all_points)


def scaled_prediction(prediction):
    """Scales the prediction

    :param prediction: the prediction to scale
    :type prediction: float
    :returns: float
    """
    if prediction < 0.05:
        return 1.0
    elif prediction > 0.4:
        return 0.0
    else:
        return linear_normalize(prediction, 0.0, 0.4).item(0)


class PatternDetection(Filter):

    """Filter for detecting pattern-like images"""

    def __init__(self):
        """Initializes a pattern detection filter"""
        self.name = 'pattern_detection'
        self.parameters = {}

    def required(self):
        return {'reduce_colors'}

    def run(self):
        """Checks if the image is pattern-like.

        :returns: float
        """
        two_color_gray_image = cv2.cvtColor(self.parameters['reduce_colors'],
                                            cv2.COLOR_BGR2GRAY)

        magnitude_spectrum = count_magnitude_spectrum(two_color_gray_image)
        return scaled_prediction(pattern_recognition(magnitude_spectrum))
