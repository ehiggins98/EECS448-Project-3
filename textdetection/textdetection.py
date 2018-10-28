#!/usr/bin/python

import sys
import os
import time

import cv2 as cv
import numpy as np

import filter


class TextDetection:

  def __init__(self, imageFile):

    self.imageFile = imageFile
    self.img = cv.imread(self.imageFile)
    self.listRect = []

  def boxCharacters(self):
      f = filter.ColorFilter()
      img = f.process(self.img)

      im2, contours, hierarchy = cv.findContours(img, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
      im2 = cv.rectangle(im2, (0,0), (100,100), (0,255,0))

      im2 = np.reshape(im2, (*im2.shape, 1))
      im2 = np.append(im2, np.append(im2, im2, axis=2), axis=2)

      for c in contours:
          x, y, w, h = cv.boundingRect(c)

          if w*h > 500:
              self.listRect.append(cv.boundingRect(c))    

  def writeRectsToImage(self):
      vis = self.img.copy()
      for rect in self.listRect:
          x, y, w, h = rect
          cv.rectangle(vis, (x, y), (x+w, y+h), (0, 255, 0), thickness=5)
      cv.imwrite('output.jpg', vis)

  def checkRectInRect(self, rectIndex1, rectIndex2, rect1Tuple, rect2Tuple):
      x1, y1, w1, h1 = rect1Tuple
      x2, y2, w2, h2 = rect2Tuple
      if x1 <= x2 and y1 <= y2 and x1+w1 <= x2+w2 and y1+h1 <= y2+w2:
        self.listRect.pop(rectIndex1)
        return True
      elif x1 >= x2 and y1 >= y2 and x1+w1 >= x2+w2 and y1+h1 >= y2+h2:
        self.listRect.pop(rectIndex2)
        return True
      else:
        return False 

text = TextDetection("image1.jpg")
text.boxCharacters()
text.writeRectsToImage()

