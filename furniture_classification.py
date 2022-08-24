# import os
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
#
# from tensorflow.keras.models import load_model
# import numpy as np
# from PIL import Image
#
# labels = ['Bed', 'Bookshelf', 'Chair', 'Desk', 'FlowerPot', 'PhotoFrame', 'Stand']
#
# model = load_model('./model/furniture_vgg16_best.h5')
#
# def predict_furniture(img_file):
#     temp_img = Image.open(img_file)
#     temp_img_re = temp_img.resize((224, 224))
#     temp_img_arr = np.array(temp_img_re)
#     temp_img = np.expand_dims(temp_img_arr, axis=0)
#
#     y_predict = model.predict(temp_img)
#
#     label = labels[y_predict[0].argmax()]
#
#     print(label)
#
#     return label
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
