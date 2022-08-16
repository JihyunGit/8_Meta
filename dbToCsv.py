import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pymongo
import glob
from bson.json_util import dumps
import json
import pandas as pd
import csv
import os

def cal_area(input_dict):
    # x = -4.16~4.71
    # 8.8
    # y = -1.45~3.57
    # 5
    # 4x4로 구역 16개 지정
    try:
        x_scale = 2.2
        y_scale = 1.25

        temp_dict = {}
        for x in range(4):
            if -4.16 + x * x_scale <= input_dict['x'] < -4.16 + (x + 1) * x_scale:
                temp_dict['x'] = x
        for y in range(4):
            if -1.45 + y * y_scale <= input_dict['y'] < -1.45 + (y + 1) * y_scale:
                temp_dict['y'] = y
        input_dict['area'] = temp_dict
        input_dict['x_coordinate'] = round(-4.16 + input_dict['area']['x'] * x_scale + x_scale / 2, 2)
        input_dict['y_coordinate'] = round(-1.45 + input_dict['area']['y'] * y_scale + y_scale / 2, 2)
    except:
        pass

    return input_dict




# DB 불러오기
client = pymongo.MongoClient("mongodb+srv://metaverse123:hongil123@accidentlyunity.ts7ta4j.mongodb.net/?retryWrites=true&w=majority", server_api=ServerApi('1'))
db = client.test
# memberDB 없으면 생성하고 있으면 불러옴, 그냥 table임
memberDB = db.members

all_member = list(memberDB.find({},{'Map':1,'_id':0}))

# now we will open a file for writing
# 디렉토리 및 파일명 설정
filename = os.path.join("./random_data.csv")

type_list = []
furstr = 'FurnitureType'
colstr = 'ColorType'

type_list.append('index')

furlist = ['Bed','BookShelf','Chair','Desk','FlowerPot','PhotoFrame','Sofa','Stand']
colorlist = ['Yellow','Blue','Green','White','Red','Brown','None']

for fur in furlist:
    for color in colorlist:
        type_list.append(fur+'/'+color)

cnt = 0

# tsv 파일 쓰기
with open(filename, "w", newline="") as result_file :
    csv_writer = csv.writer(result_file)

    ## 헤더 붙이기
    csv_writer.writerow(type_list)

    if (len(all_member) > 0):
        for data in all_member:
            ## print(data['Map'])
            user_map = json.loads(data['Map'], encoding="utf-8")
            tmp = [0] * 8 * 7
            for user_data in user_map:
                fur_num = user_data['FurnitureType']
                color_num = user_data['Index']
                real_num = fur_num * 8 + color_num + 1
                tmp[real_num] += 1
                cal_area(user_data)
            tmp[0] = cnt
            cnt += 1
            csv_writer.writerow(tmp)


def makeAreaCsv():
    filename = os.path.join("./user_map.csv")

    # 파일 생성 및 헤더 붙임
    with open(filename, "w", newline="") as result_file:
        csv_writer = csv.writer(result_file)

        header_list = ['index','Furniture','color','x','y','area_x', 'area_y']

        ## 헤더 붙이기
        csv_writer.writerow(header_list)

        cnt = 0

        if (len(all_member) > 0):
            for data in all_member:
                user_map = json.loads(data['Map'], encoding="utf-8")
                for user_data in user_map:
                    tmp = [-1] * 7
                    fur_num = user_data['FurnitureType']
                    tmp[1] = fur_num
                    color_num = user_data['Index']
                    tmp[2] = color_num
                    x_point = user_data['x']
                    tmp[3] = x_point
                    y_point = user_data['y']
                    tmp[4] = y_point
                    area_cor = cal_area(user_data)
                    # 예외 처리, x y 값이 벗어났을 때
                    try:
                        tmp[5] = area_cor['area']['x']
                        tmp[6] = area_cor['area']['y']
                    except:
                        pass

                    tmp[0] = cnt
                    cnt += 1

                    csv_writer.writerow(tmp)


df = pd.read_csv('user_map.csv')

temp_x = df.groupby(['Furniture','color'])['area_x'].value_counts()
temp_y = df.groupby(['Furniture','color'])['area_y'].value_counts()

print(temp_x)
print(temp_y)

