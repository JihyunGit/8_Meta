## 유니티에서 가구 타입, 색상 보내오면 최고 빈도수의 위치 값을 유니티로 보내준다.
from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import json

x_scale = 2.2
y_scale = 1.25

x_start = -4.16
y_start = -1.45

x_pos_list = [-3.06,-0.86,1.34,3.54]
y_pos_list = [-0.82,0.43,1.68,2.92]

# input_dict['x_coordinate'] = round(-4.16 + input_dict['area']['x'] * x_scale + x_scale / 2, 2)
# input_dict['y_coordinate'] = round(-1.45 + input_dict['area']['y'] * y_scale + y_scale / 2, 2)

## string값으로 input받음
def load_best_area(furType, colType):
    recom_best_df = pd.read_csv('./data_csv/recom_area.csv')

    # 숫자로 들어옴 furType, colType
    FurnitureType = {'Bed':0,'BookShelf':1,'Chair':2,'Desk':3,'FlowerPot':4,'PhotoFrame':5,'Sofa':6,'Stand':7}
    ColorType = {'Yellow':0,'Blue':1,'Green':2,'White':3,'Red':4,'Brown':5,'None':6}

    # 문자열이면
    # if ((type(furType)) == str):
    #     pos_df = recom_best_df[(recom_best_df['Furniture'] == int(FurnitureType[furType])) & (
    #                 recom_best_df['color'] == int(ColorType[colType]))]

    furType = int(FurnitureType[furType])

    print(furType)
    print(colType)

    test = lambda x: ColorType[colType] if ((x > 5) or (x == 0) or (x == 2)) else colType
    colType = test(furType)

    pos_df = recom_best_df[(recom_best_df['Furniture'] == int(furType)) & (recom_best_df['color'] == int(colType))]

    print('------------------------------')
    print(list(pos_df.T.to_dict()))

    pos_list = list(pos_df.T.to_dict().values())

    print(pos_list)

    recom_list = []

    for tmp in pos_list:
        recom = {}
        recom['PosX'] = x_pos_list[tmp['area_x']]
        recom['PosY'] = y_pos_list[tmp['area_y']]

        recom_list.append(recom)

    #print(recom_list)

    return recom_list