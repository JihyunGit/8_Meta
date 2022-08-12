import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pymongo
import glob
from bson.json_util import dumps
import json
import pandas as pd
import csv

# DB 불러오기
client = pymongo.MongoClient("mongodb+srv://metaverse123:hongil123@accidentlyunity.ts7ta4j.mongodb.net/?retryWrites=true&w=majority", server_api=ServerApi('1'))
db = client.test
# memberDB 없으면 생성하고 있으면 불러옴, 그냥 table임
memberDB = db.members

all_member = list(memberDB.find({},{'Map':1,'_id':0}))

# now we will open a file for writing
data_file = open('data_file.csv', 'w')

# create the csv writer object
csv_writer = csv.writer(data_file)

type_list = []
furstr = 'FurnitureType'
colstr = 'ColorType'

type_list.append('index')

for i in range(7):
    for j in range(6):
        type_list.append(furstr+str(i)+colstr+str(j))

csv_writer.writerow(type_list)

cnt = 0

# dict list형태
if (len(all_member) > 0):
    for data in all_member:
        user_map = json.loads(data['Map'])
        tmp = [0] * 43
        for user_data in user_map:
            fur_num = user_data['FurnitureType']
            color_num = user_data['Index']
            real_num = fur_num * 7 + color_num + 1
            tmp[real_num] += 1
        tmp[0] = cnt
        cnt += 1
        csv_writer.writerow(tmp)






