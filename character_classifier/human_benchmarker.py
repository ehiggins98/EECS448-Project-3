"""
A simple script for getting a human benchmark on EMNIST.
"""
import random as rand
import numpy as np
import cv2 as cv

images = np.load('dev_data.npy')
labels = np.load('dev_labels.npy')

correct = 0
total = 0

while True:
    index = rand.randint(0, np.size(images, axis=0)-1)
    label = labels[index]
    cv.imshow('Image', images[index])
    key = cv.waitKey(0)

    if key == 13:
        break

    if label <= 9:
        label += 48
    elif label >= 10 and label <= 35:
        label += 55
    else:
        label += 61

    label = chr(label)
    key = chr(key)
    if label == key or label == 'C' and key == 'c' or label == 'I' and key == 'i' or label == 'J' and key == 'j' or label == 'K' and key == 'k' or label == 'L' and key =='l' or label == 'M' and key == 'm' or label == 'O' and key =='o' or label == 'P' and key =='p' or label == 'S' and key == 's' or label == 'U' and key == 'u' or label == 'V' and key == 'v' or label == 'W' and key == 'w' or label == 'X' and key == 'x' or label == 'Y' and key == 'y' or label == 'Z' and key == 'z':
        correct += 1
    else:
        print(label, key)
    total += 1

print(correct, total, correct/total)
