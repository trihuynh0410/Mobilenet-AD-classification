# -*- coding: utf-8 -*-
"""Mobilenet

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1MEVQf2-BcEfxiMxNF-3Hx4FtfMUBrlkw
"""

from google.colab import drive
drive.mount("/content/gdrive", force_remount = True)

# Commented out IPython magic to ensure Python compatibility.
# %cd "/content/gdrive/MyDrive/AdvAI/Final/Alzheimer_s_Disease_Neuroimaging_ADNI_Dataset"

import warnings
warnings.filterwarnings ("ignore")

from tensorflow.keras import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense

from tensorflow.keras.applications import MobileNet
from tensorflow.keras.layers import Input, GlobalAveragePooling2D,AveragePooling2D, Flatten, Dense, Dropout, DepthwiseConv2D
from tensorflow.keras.models import Model

import matplotlib.pyplot as plt
import matplotlib.image as img
image=img.imread("/content/gdrive/MyDrive/AdvAI/Final/Alzheimer_s_Disease_Neuroimaging_ADNI_Dataset/test/ad/ADNI_006_S_4153_MR_Axial_T2-Star__br_raw_20130916153059956_31_S200932_I390347.jpg")
plt.figure()
plt.imshow(image)
plt.colorbar()
plt.show()

input_shape = (256, 256, 3) 
class_number = 2

mbntBase = MobileNet(weights = 'imagenet', include_top = False, input_tensor = Input(shape = input_shape))
mbntBase.summary()

# define a model
model = mbntBase.output
model = GlobalAveragePooling2D()(model)
model = Dense(2, activation='softmax')(model)

clfModel = Model(inputs=mbntBase.input, outputs=model)

# freezing all layers except for last Conv block (Conv5)
for _ in mbntBase.layers:
    if not _.name.startswith('conv5_'):
        _.trainable=False
    
clfModel.compile(optimizer = "adam",
                   loss = "binary_crossentropy", 
                   metrics = ["accuracy"])

from tensorflow.keras.preprocessing.image import ImageDataGenerator
train_datagen = ImageDataGenerator(rescale= 1./255)
test_datagen = ImageDataGenerator(rescale= 1./255)

from tensorflow.keras.applications.mobilenet import preprocess_input

training_set = train_datagen.flow_from_directory("/content/gdrive/MyDrive/AdvAI/Final/Alzheimer_s_Disease_Neuroimaging_ADNI_Dataset/train",
                                                 target_size = input_shape[:2],
                                                 batch_size = 32,
                                                color_mode="rgb",
                                                class_mode = "categorical")

labels = (training_set.class_indices)
labels = dict((v,k) for k,v in labels.items())
print(labels)

test_set = test_datagen.flow_from_directory("/content/gdrive/MyDrive/AdvAI/Final/Alzheimer_s_Disease_Neuroimaging_ADNI_Dataset/test",
                                            target_size = input_shape[:2],
                                            batch_size = 32,
                                            color_mode="rgb",
                                            class_mode = "categorical"
                                            )

from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

callback = [EarlyStopping(monitor= "val_loss", patience = 5),
            ModelCheckpoint("Model_checkpoint5_q3.h5", save_best_only = True)] # edit model name

history = clfModel.fit(training_set, steps_per_epoch = len(training_set),
               epochs = 5,
               validation_data = test_set,
               validation_steps = len(test_set),
                verbose = 1)

"""Predict"""

loaded_model = Model(inputs=mbntBase.input, outputs=model)

# Loads the weights
loaded_model.load_weights('Model_checkpoint5_q3.h5')

import cv2
img = cv2.imread("/content/gdrive/MyDrive/AdvAI/Final/Alzheimer_s_Disease_Neuroimaging_ADNI_Dataset/train/ad/ADNI_006_S_4153_MR_Axial_T2-Star__br_raw_20130916153021214_26_S200932_I390347.jpg")
plt.axis("off")
plt.imshow(img)
plt.show()

import numpy as np

img = np.expand_dims(img, axis=0)
a=loaded_model.predict(img)
a.argmax(axis=1)
labels[a.argmax(axis=1)[0]]

"""### Showing validation"""

import matplotlib.pyplot as plt
plt.figure()
plt.plot(history.history['accuracy']) 
plt.plot(history.history['val_accuracy'])
plt.title('Test acc and loss accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'])
plt.show()

# Show test set
plt.figure()
plt.plot(history.history['val_loss'])
plt.plot(history.history['val_accuracy'])
plt.title('Test Loss & Test Accuracy')
plt.ylabel('Values')
plt.xlabel('Epoch')
plt.legend(['Test Loss', 'Test Acc'])
plt.show()

# show training set
plt.figure()
plt.plot(history.history['loss'])
plt.plot(history.history['accuracy'])
plt.title('Loss & Accuracy')
plt.ylabel('Values')
plt.xlabel('Epoch')
plt.legend(['Loss', 'Acc'])
plt.show()