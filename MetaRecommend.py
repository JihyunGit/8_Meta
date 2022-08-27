import pandas as pd
import numpy as np
import json
import csv
import os
from sklearn.metrics.pairwise import cosine_similarity

## 메타버스 월드의 가구 추천

## CSV파일 만들기
def MakeRandomCSV():
    ## 서랍장 10개, 책상 7개, 화분 4개, 액자6개
    furlist = ['Bed','Chair', 'Sofa', 'Stand']
    non_color_furlist = ['BookShelf', 'Desk', 'FlowerPot']
    colorlist = ['Yellow', 'Blue', 'Green', 'White', 'Red', 'Brown']
    non_color_furlist_num = {'BookShelf': 10, 'Desk': 7, 'FlowerPot': 4}

    num_row = 300
    num_column = len(furlist) * len(colorlist) + sum(non_color_furlist_num.values())

    size = (num_row, num_column)
    random_list = np.random.randint(0, 2, size=size)

    # 디렉토리 및 파일명 설정
    filename = os.path.join("./data_csv/random_list.csv")

    type_list = []
    furstr = 'FurnitureType'
    colstr = 'ColorType'

    type_list.append('index')

    ## make column names
    for fur in furlist:
        for color in colorlist:
            type_list.append(fur + '/' + color)
    for fur in non_color_furlist:
        for num in range(non_color_furlist_num[fur]):
            type_list.append(fur + '/' + str(num))
    print(type_list)

    # tsv 파일 쓰기
    with open(filename, "w", newline="") as result_file:
        csv_writer = csv.writer(result_file)

        ## 헤더 붙이기
        csv_writer.writerow(type_list)

        tmp = [0] * num_row * num_column

        ## 바디 붙이기
        for cnt, row in enumerate(random_list):
            tmp[1:] = row
            tmp[0] = cnt
            cnt += 1
            csv_writer.writerow(tmp)

# 만들어진 코사인 유사도 맵에 원하는 가구타입/색상 입력하면 10개의 결과 리턴해줌
# 넣은 가구 타입 제외하고 추천, bed는 bed제외하고 추천
def recommend_stuff(df, title):
    title_str = title.split('/')[0]
    tmp_df = df[~df.index.str.contains(title_str)]
    return tmp_df[title].sort_values(ascending=False)[1:11]


## 메타버스 월드 내 가구 선호도 코사인 유사도 csv 파일 만들기
def MakeMetaFurnitureCosine():
    df = pd.read_csv('./data_csv/random_list.csv')
    df = df.iloc[:, 1:]
    df = df.fillna(0).astype(int)

    similarity_rate = cosine_similarity(df.T, df.T)

    similarity_df = pd.DataFrame(data=similarity_rate, index=df.T.index, columns=df.T.index)

    similarity_df.to_csv('./data_csv/result.csv')

    return similarity_df

## 추천된 가구의 위치 좌표// 원래 가구 위치 좌표 x,y
def rec_fur_position(furname=None, pos=None):
    df = MakeMetaFurnitureCosine()
    recommend_item = recommend_stuff(df, furname).index[0]
    put_fur_pos = pos
    rec_fur_pos = 0

    if put_fur_pos[1] <= 2.0:
        rec_fur_pos = put_fur_pos + np.array([0, 1.2])
    else:
        rec_fur_pos = put_fur_pos + np.array([0, -1.1])

    return recommend_item, rec_fur_pos











