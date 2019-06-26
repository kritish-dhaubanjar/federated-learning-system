#!/usr/bin/env python

from __future__ import absolute_import, division, print_function, unicode_literals


from flask import Flask, render_template, request, jsonify
from server import Server
import json

# TensorFlow and tf.keras
import tensorflow as tf
from tensorflow import keras

from tensorflow.keras.models import Sequential, model_from_json
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.layers import Embedding
from tensorflow.keras.layers import Conv1D, GlobalAveragePooling1D, MaxPooling1D

import pandas
import numpy as np

app = Flask(__name__)

server = Server()

@app.route("/", methods=['GET', 'POST'])
def index():
    message = ''
    if request.method == 'POST':
        message = "\nFederation ID: " + request.form['fed_id'] \
            + "\nDevices started: " + request.form['n_devices']
    return render_template('index.html', message=message)

@app.route("/create-federation", methods=['GET'])
def create_federation():
    server.create_federation()
    return render_template('index.html')

@app.route("/tf-test", methods=['GET'])
def train_tf():
    digits_mnist = keras.datasets.mnist

    (X_train, y_train), (X_test, y_test) = digits_mnist.load_data()
    X_train = X_train / 255.0
    X_test = X_test / 255.0

    model = keras.Sequential([
            keras.layers.Flatten(input_shape=(28, 28)),
            keras.layers.Dense(128, activation=tf.nn.relu),
            keras.layers.Dense(10, activation=tf.nn.softmax)
        ])
    model.compile(optimizer='adam',
                    loss='sparse_categorical_crossentropy',
                    metrics=['accuracy'])

    model.fit(X_train, y_train, epochs=1, verbose=0)
    res = model.evaluate(X_test, y_test)
    return render_template('index.html', message=res)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5001)