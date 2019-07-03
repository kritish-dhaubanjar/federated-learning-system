import json
import requests

from time import sleep

# TensorFlow and tf.keras
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import model_from_json

# Helper libraries
import numpy as np

class Device:
    def __init__(self, name):
        self.id = None
        self.name = name
        #self.srv_url = 'http://192.168.42.141:5001'
        self.srv_url = 'http://127.0.0.1:5001'
        self.srv_url = 'http://192.168.1.2:5001'
        

        self.connected = False
        self.initiated = False
        self.data_transfered = False
        self.round_trained = False
        self.ready = False


    def get_model_config(self):
        return self.model.to_json()
    
    def set_model_config(self, keras_config_json):
        self.model = model_from_json(keras_config_json)
        self.model.compile(optimizer='adam',
                            loss='sparse_categorical_crossentropy',
                            metrics=['accuracy'])

    def set_training_data(self, X_train, y_train):
        self.X_train = X_train
        self.y_train = y_train

    def set_global_weights(self, global_weights):
        self.model.set_weights(global_weights)

    def train_model(self):
        self.model.train_on_batch(self.X_train, self.y_train)

    def get_model_weights(self):
        return self.model.get_weights()

    def run(self):
        while True:

            if not self.connected:
                try:
                    response = requests.get(self.srv_url + '/connect')

                    print("Status: ", response.status_code, "Headers: ", response.headers['content-type'])
                    if response.status_code == 200:
                        self.connected = True
                        self.id = response.json()

                except Exception as error:
                    print(error)    
            
            elif self.connected and not self.initiated:
                try:
                    response = requests.get(self.srv_url + '/config')

                    if response.status_code == 200:
                        config = json.dumps(response.json())
                        self.set_model_config(config)
                        self.initiated = True

                except Exception as error:
                    print(error)

            elif self.initiated and not self.data_transfered:
                try:
                    response = requests.get(self.srv_url + '/data')
                    
                    if response.status_code == 200:
                        json_data = response.json()
                        self.X_train = np.array(json_data['X_train'])
                        self.y_train = np.array(json_data['y_train'])
                        print(self.X_train.shape, self.y_train.shape)
                        #print(type(json_data), len(json_data['X_train'][0][0]))
                        self.data_transfered = True
                        self.ready = True

                except Exception as error:
                    print(error)

            elif self.ready:
                try:
                    params = {}
                    params['id'] = self.id
                    response = requests.get(self.srv_url + '/ready', params=params)

                    if response.status_code == 200:
                        print("Status: Ready")
                        global_weights = response.json()
                        if response.json().get('all_ready'):
                            print("All is ready")
                        else:
                            print('Not all is ready')
                        self.ready = False
                        self.round_trained = False
                
                except Exception as error:
                    print(error)

            elif not self.round_trained:
                self.model.fit(self.X_train, self.y_train, epochs=1)
                self.round_trained = True

            elif self.round_trained and not self.ready:
                try:
                    data = {}
                    weights = self.model.get_weights()

                    weights = [ w.tolist() for w in weights ]

                    data['weights'] = weights
                    data['id'] = self.id
                    response = requests.post(self.srv_url + '/round', data=data)

                    if response.status_code == 200:
                        print("response: ", response.json())
                        self.ready = True

                except Exception as error:
                    print(error)


            waiting = 2
            print("Waiting {} sec for next response".format(waiting))
            sleep(waiting)

