import tensorflow as tf
import numpy as np
import re
import math
import random
import cv2 as cv
from os import listdir
from os.path import isfile, join

data_files = ['train_images_balanced.npy', 'test_images_balanced.npy']
label_files = ['train_labels_balanced.npy', 'test_labels_balanced.npy']

#dev_writer = tf.python_io.TFRecordWriter('dev.tfrecord')
test_writer = tf.python_io.TFRecordWriter('test.tfrecord')
train_writer = tf.python_io.TFRecordWriter('train.tfrecord')
for (image_file, label_file) in zip(data_files, label_files):
    images = np.load(image_file)
    labels = np.load(label_file)
    examples = []

    for i in range(0, np.size(images, axis=0)):
        img_flat = images[i].astype(np.uint8).flatten().tostring()
        features = {
            'label': tf.train.Feature(int64_list=tf.train.Int64List(value=labels[i].astype(np.int64))),
            'image': tf.train.Feature(bytes_list=tf.train.BytesList(value=[img_flat]))
        }
        tf_features=tf.train.Features(feature=features)
        example = tf.train.Example(features=tf_features)
        examples.append(example)

    for j in range(0, len(examples)):
        if image_file == 'train_images_balanced.npy':
            train_writer.write(examples[j].SerializeToString())
        else:
            test_writer.write(examples[j].SerializeToString())
train_writer.close()
test_writer.close()
