import requests
import json
import re
import time
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter, Retry

def relative_product(str):
    client_id = 'bdpWYU7e70Thq9gFsYAU'
    client_secret = '9JU2hmkHTD'

    naver_open_api = 'https://openapi.naver.com/v1/search/shop.json?query=' + str
    header_params = {"X-Naver-Client-Id":client_id, "X-Naver-Client-Secret":client_secret}

    res = requests.get(naver_open_api, headers=header_params)

    url = "https://search.shopping.naver.com/catalog/"

    product_list = []

    item_information = []
    if res.status_code == 200:
        data = res.json()
        # 검색 상품 중 상위 것만
        if (len(data) > 0):

            item = data['items'][0]
            id = item['link'].split('=')[1]
            re_link = url + id
            print(re_link)

            # 링크 다시 연결
            res = requests.get(re_link)

            time.sleep(1)

            bs = BeautifulSoup(res.content, "html.parser")
            # 함께 찾는 상품 목록
            result = bs.find('div', id='section_recommend_related')

            if (result):
                tmp_list = result.find_all('li')
                for tmp in tmp_list:
                    product_dict = {}
                    a_tag = tmp.find('a')
                    url = a_tag.get('href')
                    img_src = a_tag.find('img').get('src')
                    div_tag = tmp.find('div')
                    name = div_tag.find('a').text
                    price = div_tag.find('div').find('a').text
                    price = price.strip('최저 ').strip('원')

                    product_dict['Link'] = url
                    product_dict['Image'] = img_src
                    product_dict['Title'] = name
                    product_dict['Price'] = price
                    # 관련된 상품의 이름
                    product_dict['Relative'] = str

                    product_list.append(product_dict)

    return product_list