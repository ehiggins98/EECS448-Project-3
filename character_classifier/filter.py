"""
Contains utilities for thresholding a BGR image.
"""
import cv2
import numpy
import math
from enum import Enum

class ColorFilter:
    """
    Contains utilities for thresholding a BGR image.
    """

    def __init__(self):
        """
        Initializes all values to presets or None if need to be set
        """

        self.__hsv_threshold_hue = [19.424463519089514, 180.0]
        self.__hsv_threshold_saturation = [27.51798561151079, 255.0]
        self.__hsv_threshold_value = [0.0, 255.0]

        self.hsv_threshold_output = None


    def process(self, source0):
        """
        Runs the pipeline and sets all outputs to new values.

        :param source0: The BGR image to process.
        :type source0: np.ndarray
        """
        # Step HSV_Threshold0:
        self.__hsv_threshold_input = source0
        (self.hsv_threshold_output) = self.__hsv_threshold(self.__hsv_threshold_input, self.__hsv_threshold_hue, self.__hsv_threshold_saturation, self.__hsv_threshold_value)
        return self.hsv_threshold_output

    @staticmethod
    def __hsv_threshold(input, hue, sat, val):
        """
        Threshold an image based on hue, saturation, and value ranges.
        
        :param input: A BGR image.
        :type input: np.ndarray
        :param hue: A list containing only the min and max hue.
        :type hue: [float]
        :param sat: A list containing only the min and max saturation.
        :type sat: [float]
        :param val: A list containing only the min and max value.
        :type val: [float]
        :returns: A black and white np.ndarray representing the thresholded image.
        """
        out = cv2.cvtColor(input, cv2.COLOR_BGR2HSV)
        return cv2.inRange(out, (hue[0], sat[0], val[0]),  (hue[1], sat[1], val[1]))
