import numpy as np
import cv2 as cv

emnist_train = np.load('train_data.npy')
emnist_train_labels = np.load('train_labels.npy')
emnist_dev = np.load('dev_data.npy')
emnist_dev_labels = np.load('dev_labels.npy')
emnist_test = np.load('test_data.npy')
emnist_test_labels = np.load('test_labels.npy')
ext = np.load('filtered_images.npy')
ext_labels = np.load('filtered_labels.npy')

class_counts = {}

ext *= 255
ext[ext > 255] = 255
ext = ext.astype(np.uint8)
ext_labels = ext_labels.astype(np.uint8)

cv.imshow('test', ext[0])
cv.waitKey(0)

images = np.concatenate([emnist_train, emnist_dev, emnist_test], axis=0)
labels = np.concatenate([emnist_train_labels, emnist_dev_labels, emnist_test_labels], axis=0)

output_images = np.zeros((0, 32, 32), dtype=np.uint8)
output_labels = np.zeros((0, 1), dtype=np.uint8)

for i in range(np.size(images, axis=0)):
    if i % 100 == 0:
        print(np.shape(output_images), np.shape(output_labels))
    if labels[i][0] in class_counts and class_counts[labels[i][0]] < 451:
        class_counts[labels[i][0]] += 1
        output_images = np.append(output_images, np.reshape(images[i], (1, 32, 32)), axis=0)
        output_labels = np.append(output_labels, np.reshape(labels[i], (1, 1)), axis=0)
    elif labels[i][0] not in class_counts:
        class_counts[labels[i][0]] = 1
        output_images = np.append(output_images, np.reshape(images[i], (1, 32, 32)), axis=0)
        output_labels = np.append(output_labels, np.reshape(labels[i], (1, 1)), axis=0)

output_images = np.append(output_images, ext, axis=0)
output_labels = np.append(output_labels, np.reshape(ext_labels, (np.size(ext_labels), 1)), axis=0)

np.save('balanced_images.npy', output_images)
np.save('balanced_labels.npy', output_labels)
