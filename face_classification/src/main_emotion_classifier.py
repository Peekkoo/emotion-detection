import os
import shutil
import sys

import cv2
from keras.models import load_model
import numpy as np

from utils.inference import detect_faces
from utils.inference import draw_text
from utils.inference import draw_bounding_box
from utils.inference import apply_offsets
from utils.inference import load_detection_model
from utils.inference import load_image

def get_labels(dataset_name):
    if dataset_name == 'fer2013':
        return {0: 'angry', 1: 'disgust', 2: 'fear', 3: 'happy',
                4: 'sad', 5: 'surprise', 6: 'neutral'}
    elif dataset_name == 'imdb':
        return {0: 'woman', 1: 'man'}
    elif dataset_name == 'KDEF':
        return {0: 'AN', 1: 'DI', 2: 'AF', 3: 'HA', 4: 'SA', 5: 'SU', 6: 'NE'}
    else:
        raise Exception('Invalid dataset name')

def preprocess_input(x, v2=True):
    x = x.astype('float32')
    x = x / 255.0
    if v2:
        x = x - 0.5
        x = x * 2.0
    return x

def process():

    # parameters for loading data and images
    image_path = sys.argv[1]
    detection_model_path = "C:/Users/lifei/Downloads/haarcascade_frontalface_default.xml"
    emotion_model_path = 'C:/Users/lifei/Downloads/fer2013_mini_XCEPTION.102-0.66.hdf5'
    emotion_labels = get_labels('fer2013')
    font = cv2.FONT_HERSHEY_SIMPLEX

    # hyper-parameters for bounding boxes shape
    emotion_offsets = (0, 0)

    # loading models
    face_detection = load_detection_model(detection_model_path)
    emotion_classifier = load_model(emotion_model_path, compile=False)

    # getting input model shapes for inference
    emotion_target_size = emotion_classifier.input_shape[1:3]

    frames_dir = './.tmp'
    if image_path[-3:] in ['jpg', 'png']:
        images_list = [image_path]
    else:
        if os.path.exists(frames_dir):
            shutil.rmtree(frames_dir)
        os.mkdir(frames_dir)
        os.system('ffmpeg -i {} {}/$frame_%010d.jpg'.format(image_path, frames_dir))
        images_list = [os.path.join(frames_dir, f) for f in sorted(os.listdir(frames_dir))]

    output = []
    outputConf = []
    outputConfInt = -1

    for image_path_, image_path in enumerate(images_list):
        # loading images
        gray_image = load_image(image_path, grayscale=True)
        gray_image = np.squeeze(gray_image)
        gray_image = gray_image.astype('uint8')

        faces = detect_faces(face_detection, gray_image)

        tmp = []
        tmpConf = []
        for face_coordinates_, face_coordinates in enumerate(faces):

            x1, x2, y1, y2 = apply_offsets(face_coordinates, emotion_offsets)
            gray_face = gray_image[y1:y2, x1:x2]

            try:
                gray_face = cv2.resize(gray_face, (emotion_target_size))
            except:
                continue

            gray_face = preprocess_input(gray_face, True)
            gray_face = np.expand_dims(gray_face, 0)
            gray_face = np.expand_dims(gray_face, -1)


            predictions = emotion_classifier.predict(gray_face)
            emotion_label_arg = np.argmax(predictions)  # Get predicted emotion index
            emotion_text = emotion_labels[emotion_label_arg]  # Get emotion label
            confidence = predictions[0][emotion_label_arg]  # Get confidence for the predicted emotion

            tmp.append(emotion_text)
            tmpConf.append(confidence)

        if tmpConf:
            output.append(tmp)
            outputConf.append(tmpConf)
        else:
            output.append(['none'])

    # Calculate outputConfInt based on accumulated outputConf
    if outputConf:
        outputConf = np.mean([np.mean(conf_list) for conf_list in outputConf])
        outputConfInt = int(100 * outputConf)
    else:
        outputConfInt = -1  # Set fallback if no confidence values exist

    if os.path.exists(frames_dir):
        shutil.rmtree(frames_dir)

    return output, outputConfInt


if __name__ == "__main__":
    output, outputConf = process()
    if (outputConf != -1):
        OneD_output = [item for sublist in output for item in sublist]
        log_content = f"{outputConf}\n"  
        log_content += '\n'.join(OneD_output)  # Add each emotion on a new line
        with open("oemotion.log", "w") as log_file:
            log_file.write(log_content)
        print("Log file created successfully!")
    else:
        print("No data")