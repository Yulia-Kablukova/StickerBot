import pickle

import cv2
import os
import numpy as np
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
image_dir = os.path.join(BASE_DIR, "images")

face_cascade = cv2.CascadeClassifier('cascades\haarcascades\haarcascade_frontalface_alt2.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()

current_id = 0
label_ids = {}
y_labels = []
x_train = []

directory = os.fsencode(image_dir)

for file in os.listdir(directory):
    if file.decode('utf-8').endswith('.webp'):
        path = os.path.join(image_dir.encode(), file)
        label = os.path.splitext(file.decode("utf-8"))[0]

        if not label in label_ids:
            label_ids[label] = current_id
            current_id += 1
        id_ = label_ids[label]

        pil_image = Image.open(path).convert("L")
        image_array = np.array(pil_image, "uint8")
        faces = face_cascade.detectMultiScale(image_array, scaleFactor=1.5, minNeighbors=5)

        for (x, y, w, h) in faces:
            roi = image_array[y:y + h, x:x + w]
            x_train.append(roi)
            y_labels.append(id_)

with open(r'recognizers\pickles\face-labels.pickle', 'wb') as f:
    pickle.dump(label_ids, f)

recognizer.train(x_train, np.array(y_labels))
recognizer.save(r'recognizers\face-trainner.yml')
