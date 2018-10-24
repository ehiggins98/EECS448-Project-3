#!/usr/bin/python

import sys
import os
import time

import cv2 as cv
import numpy as np

import filter

if (len(sys.argv) < 2):
  print(' (ERROR) You must call this script with an argument (path_to_image_to_be_processed)\n')
  quit()

img      = cv.imread(str(sys.argv[1]))
# for visualization
vis      = img.copy()
f = filter.ColorFilter()
img = f.process(img)

im2, contours, hierarchy = cv.findContours(img, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

im2 = np.reshape(im2, (*im2.shape, 1))
im2 = np.append(im2, np.append(im2, im2, axis=2), axis=2);

lines = []

for c in contours:
    x, y, w, h = cv.boundingRect(c)
    for l in lines:


class TextLine:
    def __init__():
        self.contours = []
        self.boundingX = -1;
    def partial_contains(c):
        x, y, w, h = cv.boundingRect(c)
        
    def addContour(c):
        x, y, w, h = cv.boundingRect(c)
        if self.boundingX == -1
            self.boundingX = x
            self.boundingY = y
            self.boundingW = w
            self.boundingH = h
        else:
            if x < self.boundingX:
                x = self.boundingX
            if y < self.boundingY:
                y = self.boundingY
            if x+w > self.boundingX + self.boundingW:
                self.boundingW = x+w
            if y+h > self.boundingY + self.boundingH:
                self.boundingH = y+h
