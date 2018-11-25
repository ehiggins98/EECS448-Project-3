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
        self.original = cv.imread(self.imageFile)
        self.listRect = []
        self.listLines = []
        self.listImages = []

    def execute(self):
        self.boxCharacters()
        self.deleteBoxinBox()
        self.genLists()
        self.sortListLines()
        self.combineVertical()
        self.sortLines()
        self.writeRectsToImage()
        self.cutImages()

   # KEEP

    def boxCharacters(self):
        f = filter.ColorFilter()
        img = f.process(self.img)
        self.img = img

        im2, contours, hierarchy = cv.findContours(
            img, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        im2 = cv.rectangle(im2, (0, 0), (100, 100), (0, 255, 0))

        im2 = np.reshape(im2, (*im2.shape, 1))
        im2 = np.append(im2, np.append(im2, im2, axis=2), axis=2)

        for c in contours:
            x, y, w, h = cv.boundingRect(c)

            if w*h > 100:
                self.listRect.append(cv.boundingRect(c))
    # KEEP

    def writeRectsToImage(self):
        vis = self.original.copy()
        counter = 0
        for line in self.listLines:
            for box in line:
                if counter % 3 == 0:
                    x, y, w, h = box
                    cv.rectangle(vis, (x, y), (x+w, y+h),
                                 (255, 0, 0), thickness=5)
                elif counter % 3 == 1:
                    x, y, w, h = box
                    cv.rectangle(vis, (x, y), (x+w, y+h),
                                 (0, 255, 0), thickness=5)
                elif counter % 3 == 2:
                    x, y, w, h = box
                    cv.rectangle(vis, (x, y), (x+w, y+h),
                                 (0, 0, 255), thickness=5)
            counter += 1
        # print(self.listRect)
        cv.imwrite('outputNewRun5.jpg', vis)

    def onSameLine(self, box1, box2):
        x1, y1, w1, h1 = box1
        x2, y2, w2, h2 = box2
        upperBound = max(y1, y2)
        lowerBound = min(y1 + h1, y2 + h2)
        lengthOverlap = lowerBound - upperBound
        shortEdge = min(h1, h2)
        if lengthOverlap/shortEdge >= .05:
            return True

        else:
            return False

    def verticalOverlap(self, box1, box2):
        x1, y1, w1, h1 = box1
        x2, y2, w2, h2 = box2
        upperBound = max(x1, x2)
        lowerBound = min(x1 + w1, x2 + w2)
        lengthOverlap = lowerBound - upperBound
        shortEdge = min(w1, w2)
        if lengthOverlap/shortEdge >= 0:
            return True

        else:
            return False

    def combineVertical(self):
        for line in self.listLines:
            # print(line)
            addToLine = []
            removeBoxes = []
            for box1 in line:
                for box2 in line:
                    if box1 != box2:
                        if self.verticalOverlap(box1, box2) == True:
                            x1, y1, w1, h1 = box1
                            x2, y2, w2, h2 = box2

                            x = min(x1, x2)
                            y = min(y1, y2)
                            h = abs(y - max(y1 + h1, y2 + h2))
                            w = abs(x - max(x1 + w1, x2 + w2))
                            newBox = (x, y, w, h)

                            addToLine.append(newBox)
                            if box1 not in removeBoxes:
                                removeBoxes.append(box1)
                            if box2 not in removeBoxes:
                                removeBoxes.append(box2)

            for box in removeBoxes:
                line.remove(box)
            for box in addToLine:
                line.append(box)

    # KEEP
    def genLists(self):
        setLines = []
        while len(self.listRect) > 0:
            setLines.append(self.setRecurse(0))
        self.listLines = setLines

    def setRecurse(self, index):
        line = []
        startingBox = self.listRect[index]
        line.append(startingBox)
        for box2 in self.listRect:
            if box2 != startingBox and self.listRect.index(box2) != self.listRect.index(startingBox) and abs(startingBox[0] - box2[0]) < 500:
                if self.onSameLine(startingBox, box2):
                    line.append(box2)

        if len(line) > index + 1:
            self.recurseNext(index + 1, line)

        for box in line:
            self.listRect.remove(box)

        return(line)

    def recurseNext(self, index, array):
        startingBox = self.listRect[index]
        for box2 in self.listRect:
            if box2 != startingBox and self.listRect.index(box2) != self.listRect.index(startingBox):
                if self.onSameLine(startingBox, box2) and box2 not in array and abs(startingBox[0] - box2[0]) < 500:
                    array.append(box2)

        if len(array) > index + 1:
            # print(array)
            self.recurseNext(index + 1, array)

    # KEEP
    def sortListLines(self):
        averageYs = []
        sortedListofLines = []
        for line in self.listLines:
            yBox = []
            for box in line:
                yBox.append(box[1])
            averageYs.append(sum(yBox)/len(yBox))

        sortedAverageYs = sorted(averageYs)
        # print(averageYs)
        # print(sortedAverageYs)
        for index, value in enumerate(sortedAverageYs):
            originalIndex = averageYs.index(value)
            sortedListofLines.append(self.listLines[originalIndex])

        self.listLines = sortedListofLines

    # KEEP

    def deleteBoxinBox(self):
        for box1 in self.listRect:
            for box2 in self.listRect:
                if box1 != box2 and self.listRect.index(box1) != self.listRect.index(box2):
                    x1, y1, w1, h1 = box1
                    x2, y2, w2, h2 = box2
                    if x1 < x2 and y1 < y2 and x1 + w1 > x2 + w2 and y1 + h1 > y2 + h2:
                        self.listRect.remove(box2)

    def sortLines(self):
        for line in self.listLines:
            line.sort(key=lambda tup: tup[0])

    def cutImages(self):
        listImages = []
        maxDimension = 0
        maxLine = -1
        maxBox = -1
        for lineIndex, line in enumerate(self.listLines):
            lineImages = []
            for boxIndex, box in enumerate(line):
                x, y, w, h = box
                if w > maxDimension:
                    maxDimension = w
                    maxBox = boxIndex
                if h > maxDimension:
                    maxDimension = h
                    maxLine = lineIndex
                img = self.img[box[1]: box[1] + box[3], box[0]: box[0] + box[2]]
                
                
                img = cv.GaussianBlur(img, (0, 0), 1)
                


                lineImages.append(img)
            listImages.append(lineImages)
        self.listImages = listImages
        
        if maxDimension % 2 == 1:
            maxDimension += 1
        
        listProcessedImages = np.zeros((0, 32, 32))
        
        for lineIndex, line in enumerate(self.listLines):
            for boxIndex, box in enumerate(line):
                newImg = np.zeros((maxDimension, maxDimension))
                x, y, w, h = box

                yDiff = (maxDimension - h)/2
                xDiff = (maxDimension - w)/2
                yDiffInt = int((maxDimension - h)/2)
                xDiffInt = int((maxDimension - w)/2)
                adjustX = 0
                adjustY = 0

                if yDiffInt != yDiff:
                    adjustY = 1

                if xDiffInt != xDiff:
                    adjustX = 1

                np.set_printoptions(threshold=10000000)
                
                newImg[yDiffInt: maxDimension - yDiffInt - adjustY, xDiffInt: maxDimension - xDiffInt - adjustX] = self.listImages[lineIndex][boxIndex]
                
                newImg = cv.resize(newImg, (32, 32), interpolation=cv.INTER_CUBIC)
                maxNewImg = np.max(newImg)

                newImg = np.reshape(newImg, (1, 32, 32))
                newImg = (newImg/(np.max(newImg)))-0.13147026078678872
                listProcessedImages = np.append(listProcessedImages, newImg, axis = 0)

            zeroMatrix = np.zeros((1, 32, 32))
            listProcessedImages = np.append(listProcessedImages, zeroMatrix, axis = 0)

#text = TextDetection("image4.jpg")
#text.execute()
