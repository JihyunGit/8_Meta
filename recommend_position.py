import pandas as pd
import numpy as np
import os

filepath = './data_csv/user_map.csv'
df = pd.read_csv(filepath)

# db에 없는 furniture,color의 위치값들 -1,-1로 추천해서 널 에러 안 나게
df_tmp_empty = pd.DataFrame(columns=['index','Furniture','color','x','y','area_x','area_y'])

cnt = 0

for i in range(9):
    for j in range(7):
        tmp_list = [cnt,i,j,0,0,-1,-1]
        df_tmp_empty.loc[cnt] = tmp_list
        cnt += 1

df = pd.concat([df, df_tmp_empty])

temp_x = df.groupby(['Furniture','color'])[['area_x','area_y']].value_counts()

df_x = pd.DataFrame(temp_x)
df_x = df_x.rename(columns={0:'count'})

df_temp_x = df_x.reset_index()

df_sort = df_temp_x

df_sort_max = df_sort.groupby(['Furniture','color'])['count'].max()

df_max = df_sort_max.reset_index()

df_tmp_max = pd.merge(df_max, df_temp_x, how='inner', on=['Furniture', 'color', 'count'])
df_tmp_uni = df_tmp_max.drop_duplicates(subset=['Furniture','color'])

df_tmp = pd.merge(df, df_tmp_uni, how='left', on=['Furniture','color'])
df_tmp = df_tmp.rename(columns={'area_x_x':'area_x', 'area_y_x':'area_y', 'area_x_y':'recom_x', 'area_y_y':'recom_y'})

# 가구별 색상별 추천 위치 csv로 저장, max빈도수가 아니므로 여러 위치를 반환할 수 있음
df_tmp_max.to_csv('./data_csv/recom_area.csv')

# 실제 member의 가구별 색상별 추천 위치 csv로 저장
df_tmp.to_csv('./data_csv/recommend_position.csv')
df_tmp