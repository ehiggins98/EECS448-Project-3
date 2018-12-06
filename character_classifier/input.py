"""
The input pipeline for the character classifier.
"""
from os import listdir
from os.path import isfile, join
import re
import tensorflow as tf
import numpy as np
import cv2 as cv

train_file_names = ['train.tfrecord']
dev_file_names = ['test.tfrecord']
test_file_names = ['test.tfrecord']

batch_size = 1

def get_image_and_label(tensor):
    """
    Extracts the label and image from the given tensor.

    :param tensor: The `Tensor` from which to extract the label and image.
    :type tensor: tf.Tensor
    :returns: The image and label.
    """
    read_features = {
        'label': tf.FixedLenFeature((1), dtype=tf.int64),
        'image': tf.FixedLenFeature([], dtype=tf.string)
    }

    parsed_features = tf.parse_single_example(tensor, read_features)
    image = tf.reshape(tf.decode_raw(parsed_features["image"], tf.uint8), (32, 32))

    return tf.cast(image, dtype=tf.float32), tf.cast(parsed_features['label'], dtype=tf.int32)

def normalize(image):
    """
    Normalizes the given image by dividing by the max value (255) and subtracting the mean.

    :param image: The image to normalize.
    :type image: tf.Tensor
    :returns: The normalized image.
    """
    mean = tf.constant(0.13147026078678872, dtype=tf.float32) #mean across the entire dataset, as of 11/2/18
    image = tf.divide(image, 255)
    image = tf.subtract(image, mean)
    return image

def base_process(tensor):
    """
    Performs only normalization to process the given image and label.

    :param tensor: A tensor containing the image and label to process.
    :type tensor: tf.Tensor
    :returns: The normalized image and its corresponding label.
    """
    image, label = get_image_and_label(tensor)
    return normalize(image), label

def process(tensor):
    """
    Performs full processing on the given image and label for use during training. This includes randomly cropping
    the image, randomly scaling the image, and randomly rotating the image to an angle between 0 and 10 degrees.

    :param tensor: A tensor containing the image and label to process.
    :type tensor: tf.Tensor
    :returns: The processed tensor and its corresponding label. 
    """
    max_angle = tf.constant(0.174533) # 10 degrees in radians
    thresh = tf.constant(70, dtype=tf.float32)
    image, label = get_image_and_label(tensor)

    mask = tf.ones((28, 28))

    hpad, vpad = (tf.random_uniform([1], maxval=5, dtype=tf.int32), tf.random_uniform([1], maxval=5, dtype=tf.int32))
    scale = tf.random_uniform([1], maxval=5, dtype=tf.int32)
    angle = tf.random_uniform([1], maxval=max_angle, dtype=tf.float32)

    mask_paddings = tf.convert_to_tensor([[hpad[0], 4-hpad[0]], [vpad[0], 4-vpad[0]]])
    scale_paddings = tf.convert_to_tensor([[tf.floor(scale[0]/2), tf.ceil(scale[0]/2)], [tf.floor(scale[0]/2), tf.ceil(scale[0]/2)]])
    mask = tf.pad(mask, mask_paddings)
    mask = tf.cast(mask, dtype=tf.float32)

    image = tf.multiply(image, mask)

    image = tf.reshape(image, (32, 32, 1))
    image = tf.image.resize_images(image, (32-scale[0], 32-scale[0]), method=tf.image.ResizeMethod.BICUBIC)
    image = tf.reshape(image, (tf.shape(image)[0], tf.shape(image)[1]))
    image = tf.pad(image, tf.cast(scale_paddings, dtype=tf.int32))
    image = tf.contrib.image.rotate(image, angle[0])

    condition = tf.cast(tf.greater(image, thresh), dtype=tf.float32)
    image = tf.multiply(image, condition)

    return normalize(image), label

def process_dataset(dataset, process_fn):
    """
    Creates operations for processing batches of data.

    :param dataset: The dataset to process.
    :type dataset: tf.data.Dataset
    :param process_fn: The function to apply to elements of the dataset.
    :type process_fn: function
    :returns: Operations for processing the batches of data.
    """
    dataset = dataset.map(map_func=process_fn, num_parallel_calls=4)
    dataset = dataset.shuffle(buffer_size=5096)
    dataset = dataset.repeat()
    dataset = dataset.batch(512)
    dataset = dataset.prefetch(buffer_size=1024)
    return dataset;

def train_input_fn():
    """
    Provides input images and labels for the training procedure.

    :returns: Operations by which the dataset can be obtained.
    """
    dataset = tf.data.TFRecordDataset(train_file_names)
    return process_dataset(dataset, process)

def eval_input_fn():
    """
    Provides input images and labels for the evaluation procedure.

    :returns: Operations by which the dataset can be obtained.
    """
    dataset = tf.data.TFRecordDataset(dev_file_names)
    return process_dataset(dataset, base_process)

def test_input_fn():
    """
    Provides input images and labels for the testing procedure.

    :returns: Operations by which the dataset can be obtained.
    """
    dataset = tf.data.TFRecordDataset(test_file_names)
    return process_dataset(dataset, base_process)
