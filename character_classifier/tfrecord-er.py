import tensorflow as tf
import numpy as np
import re
import math
import random
import cv2 as cv
from os import listdir
from os.path import isfile, join


files = [f for f in listdir('.') if isfile(join('.', f)) and re.compile(".+\.npy").match(f)]
data_files = [f for f in files if re.compile("data[^\.]+.npy").match(f)]
label_files = [f for f in files if re.compile("labels[^\.]+.npy").match(f)]

dev_writer = tf.python_io.TFRecordWriter('dev.tfrecord')
test_writer = tf.python_io.TFRecordWriter('test.tfrecord')
file_index = 0
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

    rand_list = random.sample(range(1, len(examples)), 2500)
    dev = set(rand_list[:1250])
    test = set(rand_list[1250:])
    train_writer = tf.python_io.TFRecordWriter('train' + str(file_index) + '.tfrecord')
    for j in range(0, len(examples)):
        if j in dev:
            dev_writer.write(examples[j].SerializeToString())
        elif j in test:
            test_writer.write(examples[j].SerializeToString())

        else:
            train_writer.write(examples[j].SerializeToString())
    train_writer.close()
    file_index += 1
dev_writer.close()
test_writer.close()
