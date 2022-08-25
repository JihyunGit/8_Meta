import os
from PIL import Image
import numpy as np
from keras.models import load_model

new_model = load_model("./model/furniture_vgg16_best.h5")
labels = ['bed', 'bookshelf', 'chair', 'desk', 'flowerpot', 'photoframe', 'stand']

def predict_img(file_path):
    temp_img = Image.open(file_path)
    temp_img = temp_img.resize((224, 224))
    temp_img = np.array(temp_img)
    temp_img = np.expand_dims(temp_img, axis=0)

    ### 이미지 예측해보기
    ### 이미지 파일 종류

    y_predict = new_model.predict(temp_img)

    label = labels[y_predict[0].argmax()]
    confidence = y_predict[0][y_predict[0].argmax()]
    # print('predict: {} {:.2f}%'.format(label, confidence * 100))
    # print(y_predict[0])

    return label

## 사용법
"""
file_path = "C:\\Users\HP\\Desktop\\으자.jpg"
predict_label = predict_img(file_path)
print(predict_label)
함수에 안에서 프린트 안할거면 지울 것
"""


# file_path = "./upload_images/desk1.jpg"
# predict_label = predict_img(file_path)
# print(predict_label)