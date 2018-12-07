from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import tensorflow as tf
import cv2 as cv
import os

import input

var_map = {
    'conv2d/': 'conv2d/',
    'conv2d_1/': 'conv2d_1/'
}

class Model:
    """
    Represents the character classifier model.
    """
    def __init__(self):
        """
        Initializes the character classifier model.
        """
        self.classifier = tf.estimator.Estimator(model_fn=self.cnn_model_fn, model_dir="specific model/76 percent accuracy/model/")
        print(tf.VERSION)
    def predict(self, img):
        """
        Gets predictions for a matrix of images.

        :param img: An array of images for which to get predictions.
        :type img: np.ndarray
        :returns: A `[93, n]` matrix of class probabilities, where the element at `[i][j]` is the probability of character `j` being of class `i`
        """
        img = img.astype(np.float32)
        return self.classifier.predict(tf.estimator.inputs.numpy_input_fn(img, shuffle=False), yield_single_examples=False).__next__()

    def cnn_model_fn(self, features, labels, mode):
        """
        Builds the convolutional neural network.

        :param features: The images to propagate through the network. This must be an `[n, 32, 32]` matrix.
        :type features: np.ndarray
        :param labels: The correct labels, for training purposes.
        :type labels: np.ndarray
        :param mode: The mode in which to operate, from [`PREDICT`, `TRAIN`, `EVAL`].
        :type mode: tf.estimator.ModeKeys
        :returns: An `EstimatorSpec` defining the model to use for training, evaluation, or prediction.
        """
        input_layer = tf.reshape(features, [-1, 32, 32, 1], name='inputs')

        conv1 = tf.layers.conv2d(
            inputs=input_layer,
            filters=32,
            kernel_size=5,
            padding="same",
            trainable=False
        )

        activation = tf.nn.relu(conv1)

        conv2 = tf.layers.conv2d(
            inputs=activation,
            filters=64,
            kernel_size=5,
            padding="same",
            trainable=False
        )

        activation = tf.nn.relu(conv2)
        flat = tf.reshape(activation, [-1, 32 * 32 * 64])
        dense_1 = self.dense_dropconnect(flat, mode)

        logits = tf.layers.dense(
            inputs=dense_1,
            kernel_regularizer=self.kernel_regularizer,
            units=93
        )

        predictions = {
            "classes": tf.argmax(input=logits, axis=1),
            "probabilities": tf.nn.softmax(logits)
        }

        optimizer = tf.train.AdamOptimizer(learning_rate=0.001)

        if mode == tf.estimator.ModeKeys.PREDICT:
            return tf.estimator.EstimatorSpec(mode=mode, predictions=predictions["probabilities"])

        loss = tf.losses.sparse_softmax_cross_entropy(labels=labels, logits=logits) + tf.losses.get_regularization_loss()

        if mode == tf.estimator.ModeKeys.TRAIN:
            train_op = optimizer.minimize(loss=loss, global_step=tf.train.get_global_step())
            return tf.estimator.EstimatorSpec(mode=mode, loss=loss, train_op=train_op)

        eval_metric_ops = {
            "accuracy": tf.metrics.accuracy(labels=labels, predictions=predictions["classes"])
        }
        return tf.estimator.EstimatorSpec(mode=mode, loss=loss, eval_metric_ops=eval_metric_ops)

    def dense_dropconnect(self, input, mode):
        """
        Builds a DropConnect layer for regularization purposes.

        :param input: The input to the layer.
        :type input: tf.Tensor
        :param mode: The mode in which to build the layer, out of [`PREDICT`, `TRAIN`, `EVAL`].
        :type mode: tf.estimator.ModeKeys
        :returns: A `Tensor` containing the outputs of the layer.
        """
        keep_rate = 0.5
        dense_kernel = tf.get_variable('dense_1/kernel', [65536, 300], dtype=tf.float32, trainable=True, regularizer=self.kernel_regularizer)
        dense_kernel = tf.layers.dropout(dense_kernel, rate=1-keep_rate, training = mode == tf.estimator.ModeKeys.TRAIN) * keep_rate
        dense_bias = tf.get_variable('dense_1/bias', [300], dtype=tf.float32, trainable=True)
        dense = tf.matmul(input, dense_kernel)
        dense = tf.add(dense, dense_bias)
        activation = tf.nn.relu(dense)
        return dense

    def kernel_regularizer(self, weights):
        """
        Adds additional L2 regularization to the given weights.

        :pararm weights: The weights to regularize.
        :type weights: tf.Tensor
        :returns: The regularization loss, computed over the weights.
        """
        regularization = 0.001
        result = tf.reduce_sum(tf.square(weights)) * regularization
        return result
