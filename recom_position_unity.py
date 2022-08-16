## 유니티에서 가구 타입, 색상 보내오면 최고 빈도수의 위치 값을 유니티로 보내준다.

import pandas as pd
import numpy as np

recom_best_df = ''

x_scale = 2.2
y_scale = 1.25

def load_best_area(furType, colType):
    recom_best_df = pd.read_csv('./data_csv/recom_area.csv')
    # 조건을 만족하는 것들, 리스트일 확률도 있음
    pos_list = recom_best_df[(recom_best_df['Furniture'] == furType) & (recom_best_df['color'] == colType)]


load_best_area(0,1)















