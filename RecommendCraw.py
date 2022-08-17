import requests
import json
import re
import time


def item_info(item_name, color_type):
    client_id = 'bdpWYU7e70Thq9gFsYAU'
    client_secret = '9JU2hmkHTD'

    item_dict = {'Bed': '침대', 'BookShelf': '책장', 'Chair': '의자', 'Desk': '책상', 'FlowerPot': '화분', 'PhotoFrame': '액자',
                 'Sofa': '소파', 'Stand': '스탠드'}
    color_dict = {'Yellow': '노란색', 'Blue': '파란색', 'Green': '초록색', 'White': '흰색', 'Red': '빨간색', 'Brown': '갈색',
                  'None': ''}

    item_color = f"{item_dict[item_name]} {color_dict[color_type]}"
    name = item_name +'_'+ color_type

    agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
    hdata = {'User_Agent':agent}

    naver_open_api = 'https://openapi.naver.com/v1/search/shop.json?query=' + item_color
    res = requests.get(naver_open_api, headers=hdata)


# for i in item_dict.keys():
#     for j in color_dict.keys():
#         item_info(i,j)

def makeJsonItem():
    item_dict = {'Chair': '의자', 'Sofa': '소파', 'Bed': '이불', 'Refrigerator': '냉장고'}
    color_dict = {'Yellow': '노란색', 'Blue': '파란색', 'Green': '초록색', 'White': '흰색', 'Red': '빨간색', 'Brown': '갈색'}
    for i in item_dict.keys():
        for j in color_dict.keys():
            item_info(i, j)
