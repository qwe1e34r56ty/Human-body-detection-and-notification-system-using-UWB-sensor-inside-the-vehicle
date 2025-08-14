import matplotlib.pyplot as plt
import tensorflow as tf
import pandas as pd
import sys
from loadCirFtDataSet import *;
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

def training(savePath, dir):
    X, y = loadCirFtDataSet(findCsvFilesInDir(dir));

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = tf.keras.Sequential([
        tf.keras.layers.Conv1D(filters=64, kernel_size=3, activation='relu', input_shape=(200, 1)),
        tf.keras.layers.MaxPooling1D(pool_size=3),
        tf.keras.layers.Conv1D(filters=64, kernel_size=3, activation='relu'),
        tf.keras.layers.MaxPooling1D(pool_size=3),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])

    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    model.fit(X_train, y_train, epochs=25, batch_size=32, validation_data=(X_test, y_test))

    plt.plot(model.history.history['loss'], label='Training Loss')
    plt.plot(model.history.history['val_loss'], label='Validation Loss')
    plt.title('Training and Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.show()

    plt.plot(model.history.history['accuracy'])
    plt.plot(model.history.history['val_accuracy'])
    plt.title('Accuracy graph')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend(['Train','Validation'])
    plt.grid()
    plt.show()

    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    tfliteModel = converter.convert();
    with open(f'{savePath}.tflite', 'wb') as f:
        f.write(tfliteModel);
        
if __name__ == "__main__":
    training("model", "dataSet");