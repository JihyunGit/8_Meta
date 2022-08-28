import numpy as np
import pandas as pd
import pymongo
from pymongo.server_api import ServerApi
import glob
import os
import json
import csv
import math

furlist = ['Bed', 'BookShelf', 'Chair', 'Desk', 'FlowerPot', 'PhotoFrame', 'Sofa', 'Stand']
colorlist = ['Yellow', 'Blue', 'Green', 'White', 'Red', 'Brown']


def LoadMapList():
    # DB 불러오기
    client = pymongo.MongoClient(
        "mongodb+srv://metaverse123:hongil123@accidentlyunity.ts7ta4j.mongodb.net/?retryWrites=true&w=majority",
        server_api=ServerApi('1'))
    db = client.test

    memberDB = db.members

    all_member = list(memberDB.find({}, {'Map': 1, '_id': 0}))

    ## 서랍장 10개, 책상 7개, 화분 4개, 액자6개
    non_color = {'BookShelf': 10, 'Desk': 7, 'FlowerPot': 4, 'PhotoFrame': 6}
    # 1,3,4,5

    col_list = []

    for fur in furlist:
        if fur in non_color.keys():
            for num in range(non_color[fur]):
                col_list.append(str(fur) + '/' + str(num))
        else:
            for color in colorlist:
                col_list.append(fur + '/' + color)

    return col_list, all_member


def MakeMemberCsv(col_list, all_member):
    filename = os.path.join("./data_csv/member_map.csv")

    with open(filename, "w", newline="") as result_file :
        csv_writer = csv.writer(result_file)

        ## 헤더 붙이기
        csv_writer.writerow(col_list)

        if (len(all_member) > 0):
            for data in all_member:
                tmp = [-1] * len(col_list)
                try:
                    user_map = json.loads(data['Map'])
                except:
                    continue
                for user_data in user_map:
                    fur_num = user_data['FurnitureType']
                    color_num = user_data['Index']
                    x = user_data['x']
                    y = user_data['y']

                    # 8부터는 벽과 타일이므로
                    if fur_num < 8:
                        try:
                            test = lambda x: colorlist[color_num] if ((x > 5) or (x == 0) or (x == 2)) else color_num
                            index = test(fur_num)
                            col_num = col_list.index(furlist[fur_num] + '/' + str(index))
                            tmp[col_num] = str(x) + '/' + str(y)
                        except:
                            continue

                print(tmp)
                csv_writer.writerow(tmp)


# 점과 점 사이의 거리 구하는 함수
def distance(x1, y1, x2, y2):
    x1 = float(x1)
    y1 = float(y1)
    x2 = float(x2)
    y2 = float(y2)
    return round(math.dist([x1,y1], [x2,y2]),4)


# 정규화를 위한 (두 가구간의 거리이지만 두 가구의 관계도가 높을 수록 혹은 그저 거리가 멀수록 크기가 커지므로 관계성이 이상해질 수 있음)
# 따라서 멀어서 커진건지 많이 더해져서 커진 것인지 구분이 되어야 함
# 많이 더해져서 커진 경우 관계성이 높은 것이고 거리가 멀어서 커진 경우 관계성이 낮아짐

# 따라서 알고리즘 만듦
# 거리를 전부 더한 값을 역수로 취해 큰 값은 작게 만들고 작은 값은 크게 만든 후
# 관계 빈도수를 곱해서 더 많이 등장할 수록 값이 커지게 만듦
# ex ) 거리 총합이 30인 가구의 관계일 경우 역수를 취하면 1/30 (0.0333)이므로 관계성이 낮아짐
# 다만 많이 등장해서 거리값이 높아진 거라면 예를 들어 빈도수 카운트 10을 곱하면 0.3333으로 관계성이 높아짐
def makeRelationCsv(col_list):
    # 사용자의 map csv
    df = pd.read_csv('./data_csv/member_map.csv', index_col=0)

    # 빈 df 생성
    tmp_arr = np.ones((len(col_list), len(col_list))) * -1
    result_df = pd.DataFrame(tmp_arr, columns=col_list, index=col_list)

    count_arr = np.ones((len(col_list), len(col_list)))

    for data in df.itertuples():
        for index1, d1 in enumerate(data):
            for index2, d2 in enumerate(data[index1+1:]):
                before_index = index1
                after_index = index1 + index2 + 1
                # 만약 가구종류가 0~30까지만 있는데 31번과 비교하려고 하면 안되므로 패스해버림
                if (after_index >= len(col_list)):
                    continue
                # -1은 해당가구를 배치하지 않은 것이므로 그런 경우 관계성은 없으므로 스킵
                if (str(d1) != '-1') & (str(d2) != '-1'):
                    x1,y1 = d1.split('/') # 비교할 가구 1의 위치
                    x2,y2 = d2.split('/') # 비교할 가구 2의 위치
                    dist = distance(x1, y1, x2, y2)

                    # 관계성을 위해 두 가구가 같은 맵에 있던 카운트 수를 저장함
                    count_arr[before_index,after_index] += 1
                    count_arr[after_index,before_index] += 1

                    result_df.iloc[before_index,after_index] += dist
                    result_df.iloc[after_index,before_index] += dist

    # 역수, 큰 값은 작게 만들고 작은 값은 크게
    new_df = np.reciprocal(result_df)

    # 관계 카운트에 따라 자주 나타났을 경우 값을 크게 해줌
    final_df = new_df * count_arr

    # result_df.to_csv('./data_csv/resultdf.csv')
    # new_df.to_csv('./data_csv/newdf.csv')
    # final_df.to_csv('./data_csv/finaldf.csv')
    # np.savetxt('./data_csv/count1.csv',count_arr,delimiter=",")

final_df = pd.read_csv('./data_csv/finaldf.csv')
final_df = final_df.set_index('Unnamed: 0')

# 관계가 높은 가구 반환
def recom_best(tmp_df, title):
    return tmp_df[title].sort_values(ascending=False)



## 사용법
# col_list, all_member = LoadMapList()
# MakeMemberCsv(col_list, all_member)
# makeRelationCsv(col_list)
# tmp = recom_best(final_df, 'Chair/White')
# print(tmp)

# 유니티에서 가구카테고리/색상 하나와 해당 사용자 맵의 정보를 보내면
# 관계가 높은 가구 중 사용자의 현재 맵에 배치된 가구와 일치하는 곳의 위치값을 보내줘야 함

# 말하자면 사용자가 현재 선택한 가구가 하얀 침대와 관계가 가장 높다면 맵에 하얀 침대가 있는지 확인 후
# 있다면 사용자의 하얀 침대가 어느 위치에 존재하는지 위치값을 유니티로 보내줘야 함
# 특히 사용자의 맵에 아무것도 없는 상태일 경우 기존의 구역 추천을 해줘야 함



# {'name': 'Desk/3', 'vaule': 0.5326160770162847, 'fur': 3, 'color': 3, 'PosX': 2.87289286, 'PosY': 1.75479341} 이런 값 반환
def ReturnRecomFurniture(user_data, furniture_type, color_type):
    result_list = []
    sorted_dict = []

    # Chair/White 형태
    recom_str = furniture_type + '/' + color_type

    # 관계가 높은 가구들 리스트 반환
    recom_list = recom_best(final_df, recom_str)

    for data in user_data:
        fur_num = data['FurnitureType']
        color_num = data['Index']
        x = data['x']
        y = data['y']

        # 색상값없는 가구들은 숫자로
        try:
            test = lambda x: colorlist[color_num] if ((x > 5) or (x == 0) or (x == 2)) else color_num
            index = test(fur_num)
            tmp_str = furlist[fur_num] + '/' + str(index)
        except:
            continue

        # 인자로 받은 가구/색상과 일치하면 리스트 추가
        for recom, value in zip(recom_list.index, recom_list):
            if tmp_str == recom:
                if value > 0:
                    result = {}
                    result['name'] = recom
                    result['vaule'] = value
                    result['fur'] = fur_num
                    result['color'] = color_num
                    result['PosX'] = x
                    result['PosY'] = y
                    result_list.append(result)
                    break

    sorted_dict = sorted(result_list, key=lambda d: d['vaule'], reverse=True)

    print(sorted_dict)

    # 가장 높은 관계성을 가진 아이템 반환
    if (len(sorted_dict) > 0):
        return sorted_dict[0]

    return sorted_dict



















