from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import tensorflow as tf

import input

tf.logging.set_verbosity(tf.logging.INFO)
initial_rate = 0.01

def cnn_model_fn(features, labels, mode):
    input_layer = tf.reshape(features, [-1, 32, 32, 1], name='inputs')

    conv1 = tf.layers.conv2d(
        inputs=input_layer,
        filters=32,
        kernel_size=5,
        padding="same"
    )

    activation = tf.nn.relu(conv1)

    conv2 = tf.layers.conv2d(
        inputs=activation,
        filters=64,
        kernel_size=5,
        padding="same"
    )

    activation = tf.nn.relu(conv2)
    flat = tf.reshape(activation, [-1, 32 * 32 * 64])

    dense = tf.layers.dense(
        inputs=flat,
        units=150,
    )
    activation = tf.nn.relu(dense)

    dropout = tf.layers.dropout(
        inputs=activation,
        rate=0.5
    )

    logits = tf.layers.dense(
        inputs=dropout,
        units=93
    )

    predictions = {
        "classes": tf.argmax(input=logits, axis=1),
        "probabilities": tf.nn.softmax(logits)
    }

    if mode == tf.estimator.ModeKeys.PREDICT:
        return tf.estimator.EstimatorSpec(mode=mode, predictions=predictions)

    loss = tf.losses.sparse_softmax_cross_entropy(labels=labels, logits=logits)

    if mode == tf.estimator.ModeKeys.TRAIN:
        learning_rate = tf.Variable(initial_rate, name='learning_rate')
        learning_rate_placeholder = tf.placeholder(tf.float32, [])

        learning_rate_hook = LearningRateHook(learning_rate, learning_rate_placeholder, loss)

        optimizer = tf.train.MomentumOptimizer(learning_rate=learning_rate, momentum=0.9)
        train_op = optimizer.minimize(loss=loss, global_step=tf.train.get_global_step())
        return tf.estimator.EstimatorSpec(mode=mode, loss=loss, train_op=train_op, evaluation_hooks=[learning_rate_hook])

    eval_metric_ops = {
        "accuracy": tf.metrics.accuracy(labels=labels, predictions=predictions["classes"])
    }
    learning_rate = tf.Variable(initial_rate, name='learning_rate')
    learning_rate_placeholder = tf.placeholder(tf.float32, [])

    learning_rate_hook = LearningRateHook(learning_rate, learning_rate_placeholder, loss)
    return tf.estimator.EstimatorSpec(mode=mode, loss=loss, eval_metric_ops=eval_metric_ops, evaluation_hooks=[learning_rate_hook])

class LearningRateHook(tf.train.SessionRunHook):
    def __init__(self, learning_rate_tensor, learning_rate_placeholder, loss):
        self.learning_rate_placeholder = learning_rate_placeholder
        self.learning_rate = 0.01
        self.learning_rate_tensor = learning_rate_tensor
        self.loss_op = loss
        self.last_loss = 0
        self.update_op = tf.assign(self.learning_rate_tensor, self.learning_rate_placeholder)

    def before_run(self, run_context):
        return tf.train.SessionRunArgs(self.loss_op, {})

    def after_run(self, run_context, run_values):
        loss = run_values.results
        if abs(loss - self.last_loss) < 0.05:
            self.learning_rate *= 0.5
        run_context.session.run(self.update_op, feed_dict={self.learning_rate_placeholder: self.learning_rate})


def main(unused_argv):
    classifier = tf.estimator.Estimator(model_fn=cnn_model_fn, model_dir="tmp/model")

    log = tf.train.LoggingTensorHook({'learning_rate'}, every_n_iter=100)

    for i in range(0, 10):
        eval_results = classifier.evaluate(input_fn=input.eval_input_fn, steps=20)
        classifier.train(
            input_fn=input.train_input_fn,
            steps=200,
            hooks=[log]
        )

if __name__ == "__main__":
    tf.app.run()
