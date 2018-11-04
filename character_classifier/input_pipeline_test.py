"""
A "test class" for the tensorflow input pipeline. You have to inspect the images manually right now,
because it's kind of hard to test rotations and such.
It could be improved to be automated in the future.
"""
import tensorflow as tf
import input
import cv2 as cv
import numpy as np

filename_queue = tf.train.string_input_producer(['train0.tfrecord'])
reader = tf.TFRecordReader()
key, value = reader.read(filename_queue)

mean = tf.constant(0.13147026078678872, dtype=tf.float32) #mean across the entire dataset, as of 11/2/18

init_op = tf.global_variables_initializer()
with tf.Session() as sess:
    sess.run(init_op)

    coord = tf.train.Coordinator()
    threads = tf.train.start_queue_runners(coord=coord)

    for i in range(0, 10):
        #img = tf.reshape(tf.decode_raw(parsed_features["train/image"], tf.uint8), (32, 32, 1))
        #label = tf.cast(parsed_features["train/label"], tf.uint8)
        processed, label = input.process(value)
        tf.Print('processed', [processed])
        processed = tf.add(processed, mean)
        processed = tf.multiply(processed, 255)
        p, l = sess.run([processed, label])
        cv.imwrite('p' + str(i) + '.jpg', p)
        print(l)
    coord.request_stop()
    coord.join(threads)
