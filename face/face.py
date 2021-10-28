import pickle
import cv2


def recognize(path, gender):
    face_cascade = cv2.CascadeClassifier(r'cascades\haarcascades\haarcascade_frontalface_alt2.xml')

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer_path = r'recognizers\face-trainner-' + gender + '.yml'
    recognizer.read(recognizer_path)

    pickle_path = r'recognizers\pickles\face-labels-' + gender + '.pickle'
    labels = {"person_name": 1}
    with open(pickle_path, 'rb') as f:
        og_labels = pickle.load(f)
        labels = {v: k for k, v in og_labels.items()}

    frame = cv2.imread(path)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.5, minNeighbors=5)
    for (x, y, w, h) in faces:
        roi_gray = gray[y:y + h, x:x + w]

        id_, conf = recognizer.predict(roi_gray)
        print(conf)
        if conf >= 45:
            name = labels[id_]
            print(name)
            return name
