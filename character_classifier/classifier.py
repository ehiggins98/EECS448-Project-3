from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import tensorflow as tf
import cv2 as cv
import os

import input

tf.logging.set_verbosity(tf.logging.INFO)
initial_rate = 0.01

var_map = {
    'conv2d/': 'conv2d/',
    'conv2d_1/': 'conv2d_1/'
}

def cnn_model_fn(features, labels, mode):
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
    batch_norm = tf.layers.batch_normalization(flat)
    dense_1 = tf.layers.dense(
        inputs=batch_norm,
        kernel_regularizer=kernel_regularizer,
        units=150
    )
    dense_2 = dense_dropconnect(dense_1, mode)

    logits = tf.layers.dense(
        inputs=dense_2,
        kernel_regularizer=kernel_regularizer,
        units=93
    )

    predictions = {
        "classes": tf.argmax(input=logits, axis=1),
        "probabilities": tf.nn.softmax(logits)
    }

    optimizer = tf.train.AdamOptimizer(learning_rate=0.001)
    tf.train.init_from_checkpoint('general model/83 percent accuracy/model3/model', var_map)

    if mode == tf.estimator.ModeKeys.PREDICT:
        hook = TestHook(features, predictions["classes"])
        return tf.estimator.EstimatorSpec(mode=mode, predictions=predictions)

    loss = tf.losses.sparse_softmax_cross_entropy(labels=labels, logits=logits) + tf.losses.get_regularization_loss()

    if mode == tf.estimator.ModeKeys.TRAIN:
        train_op = optimizer.minimize(loss=loss, global_step=tf.train.get_global_step())
        return tf.estimator.EstimatorSpec(mode=mode, loss=loss, train_op=train_op)

    eval_metric_ops = {
        "accuracy": tf.metrics.accuracy(labels=labels, predictions=predictions["classes"])
    }
    return tf.estimator.EstimatorSpec(mode=mode, loss=loss, eval_metric_ops=eval_metric_ops)

def dense_dropconnect(input, mode):
    keep_rate = 0.5
    dense_kernel = tf.get_variable('dense_2/kernel', [150, 150], dtype=tf.float32, trainable=True, regularizer=kernel_regularizer)
    dense_kernel = tf.layers.dropout(dense_kernel, rate=1-keep_rate, training = mode == tf.estimator.ModeKeys.TRAIN) * keep_rate
    dense_bias = tf.get_variable('dense_2/bias', [150], dtype=tf.float32, trainable=True)
    dense = tf.matmul(input, dense_kernel)
    dense = tf.add(dense, dense_bias)
    activation = tf.nn.relu(dense)
    return dense

def kernel_regularizer(weights):
    regularization = 0.001
    result = tf.reduce_sum(tf.square(weights)) * regularization
    return result

def main(unused_argv):
    steps_per_train = 200
    classifier = tf.estimator.Estimator(model_fn=cnn_model_fn, model_dir="tmp/model")

    for i in range(0, 100):
        classifier.train(
            input_fn=input.train_input_fn,
            steps=steps_per_train
        )
        eval_results = classifier.evaluate(input_fn=input.eval_input_fn, steps=12)
if __name__ == "__main__":
    tf.app.run()
