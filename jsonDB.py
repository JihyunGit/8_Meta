import json
import pymongo
import glob
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

client = pymongo.MongoClient("mongodb+srv://metaverse123:hongil123@accidentlyunity.ts7ta4j.mongodb.net/?retryWrites=true&w=majority", server_api=ServerApi('1'))
db = client.test

productDB = db.product
print('DB연동완료')

file_list = glob.glob('./data/*.json')
print(len(file_list))

for file_name in file_list:
    with open(file_name, "r", encoding='UTF-8') as json_file:
        json_data = json.load(json_file)

        for i in range(len(json_data)):
            json_dict = json_data[i]
            result = productDB.update({'Link': json_dict['Link']}, json_dict, upsert=True)
            print(result)

    # color_data = json_dict['Color']
    # category_data = json_dict['Category']
    # title_data = json_dict['Title']
    # link_data = json_dict['Link']
    # image_data = json_dict['Image']
    # brand_data = json_dict['Brand']
    # price_data = json_dict['Price']

















