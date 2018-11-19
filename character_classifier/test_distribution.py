"""
A "test class" for the tensorflow input pipeline. You have to inspect the images manually right now,
because it's kind of hard to test rotations and such.
It could be improved to be automated in the future.
"""
import tensorflow as tf
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

files = ['train0.tfrecord', 'train1.tfrecord', 'train2.tfrecord', 'train3.tfrecord', 'train4.tfrecord', 'train5.tfrecord', 'train6.tfrecord', 'train7.tfrecord', 'dev.tfrecord', 'test.tfrecord', ]

filename_queue = tf.train.string_input_producer(files)
reader = tf.TFRecordReader()
read_features = {
    'label': tf.FixedLenFeature([], dtype=tf.int64),
    'image': tf.FixedLenFeature([], dtype=tf.string)
}

mean = tf.constant(0.13147026078678872, dtype=tf.float32) #mean across the entire dataset, as of 11/2/18

init_op = tf.global_variables_initializer()

def read_file(file, length):
    classes = np.zeros((93))
    for i in range(0, length):
        parsed = tf.parse_single_example(value, read_features)
        features = sess.run(parsed)
        classes[features['label']] += 1

        if i % 100 == 0:
            print(i)

    return classes


with tf.Session() as sess:
    sess.run(init_op)
    train_classes = np.zeros((93))
    dev_classes = np.zeros((93))
    test_classes = np.zeros((93))

    coord = tf.train.Coordinator()
    threads = tf.train.start_queue_runners(coord=coord)

    for i in range(0, len(files)):
        key, value = reader.read(filename_queue)
        if i < 7:
            train_classes += read_file(value, 100000)
        elif i == 7:
            train_classes += read_file(value, 85492)
        elif i == 8:
            dev_classes += read_file(value, 10000)
        else :
            test_classes += read_file(value, 10000)

    train_graph = plt.bar(range(1, 94), train_classes)

    plt.subplot(121)
    dev_graph = plt.bar(range(1, 94), dev_classes)

    plt.subplot(121)
    test_graph = plt.bar(range(1, 94), test_classes)

    plt.show()
