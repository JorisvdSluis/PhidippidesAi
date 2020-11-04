# Tensorflow
import tensorflow as tf

import pathlib
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

np.set_printoptions(precision=4)

list_ds = tf.data.Dataset.list_files(os.listdir('dataset/data_road'))

# Reads an image from a file, decodes it into a dense tensor, and
# resizes it to a fixed shape
def parse_image(filename):
    parts = tf.strings.split(filename, os.sep)
    label = parts[-2]

    image = tf.io.read_file(filename)
    image = tf.image.decode_jpeg(image)
    image = tf.image.convert_image_dtype(image, tf.float32)
    image = tf.image.resize(image, [128, 128])
    return image, label


file_path = next(iter(list_ds))
image, label = parse_image(file_path)


def show(image, label):
    plt.figure()
    plt.imshow(image)
    plt.title(label.numpy().decode('utf-8'))
    plt.axis('off')


show(image, label)
