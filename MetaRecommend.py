import pandas as pd
import numpy as np
import json
import csv
import os
from sklearn.metrics.pairwise import cosine_similarity

## 메타버스 월드의 가구 추천

## CSV파일 만들기
def MakeRandomCSV():
    furlist = ['Bed', 'BookShelf', 'Chair', 'Desk', 'FlowerPot', 'PhotoFrame', 'Sofa', 'Stand']
    colorlist = ['Yellow', 'Blue', 'Green', 'White', 'Red', 'Brown', 'None']

    size = (100, len(furlist) * len(colorlist))
    random_list = np.random.randint(0, 2, size=size)

    # 디렉토리 및 파일명 설정
    filename = os.path.join("./data_csv/random_list.csv")

    type_list = []
    furstr = 'FurnitureType'
    colstr = 'ColorType'

    type_list.append('index')

    cnt = 0

    for fur in furlist:
        for color in colorlist:
            type_list.append(fur + '/' + color)

    # tsv 파일 쓰기
    with open(filename, "w", newline="") as result_file:
        csv_writer = csv.writer(result_file)

        ## 헤더 붙이기
        csv_writer.writerow(type_list)

        tmp = [0] * len(furlist) * len(colorlist)

        ## 바디 붙이기
        for row in random_list:
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



MakeRandomCSV()
# df = MakeMetaFurnitureCosine()
# result = recommend_stuff(df,'Bed/Blue')

def GetRecommendPos(category_and_color):
    df = MakeMetaFurnitureCosine()
    # category_and_color = 'Bed/Blue' 이런 형태
    result = recommend_stuff(df, category_and_color)

    # 전체 맵 좌표
    left_up = (-4.2, 2.97)
    left_down = (-4.2, -1.1)
    right_down = (4.27, -1.1)
    right_up = (4.27, 2.97)

    ## 경계선 y값 2, 더하는 값 1.2
    ## 놓은 x값
    put_fur_pos = np.array([2, 1])
    rec_fur_pos = 0

    rec_fur_pos = put_fur_pos + np.array([0, 0.75])
    if put_fur_pos[1] <= 2.0:
        rec_fur_pos = put_fur_pos + np.array([0, 1.2])
    else:
        rec_fur_pos = put_fur_pos + np.array([0, -1.1])

    print(result)
    print("추천가구:",result.index[0], "// 좌표:", rec_fur_pos)







GetRecommendPos('Sofa/Blue')
































