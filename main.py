import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from apscheduler.schedulers.background import BackgroundScheduler    # apscheduler 라이브러리 선언
import Craw
import time
import json
import pymongo
import glob
from bson.json_util import dumps
import recom_position_unity
import numpy as np
import CrawRelative
import pandas as pd
import MetaRecommend
import realClassification
import requests
import new_pos
from flask_cors import CORS, cross_origin



# DB 불러오기
client = pymongo.MongoClient("mongodb+srv://metaverse123:hongil123@accidentlyunity.ts7ta4j.mongodb.net/?retryWrites=true&w=majority", server_api=ServerApi('1'))
db = client.test
# memberDB 없으면 생성하고 있으면 불러옴, 그냥 table임
memberDB = db.members
# 상품 정보
productDB = db.product
## 추천 상품 정보
relativeDB = db.relative
## 장바구니
basketDB = db.basket
## 중고거래 게시판
usedDB = db.usedBoard

print("DB 연동 완료")

## 메타버스 월드 내 가구 추천 코사인 유사도 데이터 프레임
cosine_df = pd.read_csv('./data_csv/result.csv')
cosine_df = cosine_df.set_index('Unnamed: 0')

## ------------------ 변수들 --------------------------------------
## 스케줄
sched_num = 0

# 위치 추천 관련 x,y
x_scale = 2.2
y_scale = 1.25

x_start = -4.16
y_start = -1.45

x_pos_list = [-3.06,-0.86,1.34,3.54]
y_pos_list = [-0.82,0.43,1.68,2.92]

# 카테고리
# FlowerPot, PhotoFrame, BookShelf, Stand는 Color : None이고 Floor는 가구가 아님
furlist = ['Bed', 'BookShelf', 'Chair', 'Desk', 'FlowerPot', 'PhotoFrame', 'Sofa', 'Stand', 'Floor']
colorlist = ['Yellow', 'Blue', 'Green', 'White', 'Red', 'Brown', 'None']

## -------------------------- 함수 ---------------------------------
# 맵있는지 결과 bool값과, 맵 정보 json 형식으로 보내기
def MakeResultJson(result, data=None):
    resultDic = {
        "Result": result,
        "Map": data
    }

    return jsonify(resultDic)

def MakeRecommendResponseDataJson(imageUrl, name, link):
    dic = {
        "ImageUrl": imageUrl,
        "Link": link,
        "Name": name
    }

    return dic

# json 파일 만들고 그 관련 상품들을 DB에 저장하기
def MakeJsonToDB():
    # json 파일 만들고
    Craw.makeJsonItem()

    # json -> DB
    file_list = glob.glob('./data/*.json')
    print(len(file_list))

    for file_name in file_list:
        with open(file_name, "r", encoding='UTF-8') as json_file:
            json_data = json.load(json_file)

            for i in range(len(json_data)):
                json_dict = json_data[i]
                
                ## Product DB에 넣기
                result_prod = productDB.update({'Image':json_dict['Image']}, json_dict, upsert=True)

                ## 실제 상품과 관련된 상품을 DB에 저장
                relative_list = CrawRelative.relative_product(json_dict['Title'])

                print(relative_list)

                for relative in relative_list:
                    ## 이미지 링크 기준으로 중복이면 추가 안 함
                    result = relativeDB.update({'Image':relative['Image']}, relative, upsert=True)


## 이미 있는 json파일들 불러와서 관련 상품 찾고 DB에 저장
def FromJsonToDB():
    file_list = glob.glob('./data/*.json')
    print(len(file_list))
    
    for file_name in file_list:
        with open(file_name, "r", encoding='UTF-8') as json_file:
            json_data = json.load(json_file)

            for i in range(len(json_data)):
                json_dict = json_data[i]

                ## Product DB에 넣기
                result_prod = productDB.update({'Image':json_dict['Image']}, json_dict, upsert=True)

                ## 실제 상품과 관련된 상품들 불러오기
                relative_list = CrawRelative.relative_product(json_dict['Title'])

                print(relative_list)

                for relative in relative_list:
                    result = relativeDB.update({'Image':relative['Image']}, relative, upsert=True)

# 이미 저장된 상품들의 관련 상품들 불러와서 DB에 저장
def LoadDBProduct():
    cursor = productDB.find({})
    for document in cursor:
        relative_list = CrawRelative.relative_product(document['Title'])

        for relative in relative_list:
            result = relativeDB.update({'Image':relative['Image']}, relative, upsert=True)


## FurnitureType, index의 숫자 값을 받아서
## dict형태로 반환
def ReturnCategory(FurnitureType, ColorType):
    tmp_dict = {}
    tmp_dict['furniture'] = furlist[FurnitureType]
    tmp_dict['color'] = colorlist[ColorType]

    return tmp_dict

## dict형을 가구타입/컬러타입 형태의 문자열로 변경
def MakeStringCategory(tmp_dict):
    return str(tmp_dict['furniture']+'/'+tmp_dict['color'])


## 메타버스 월드 내 가구 추천 결과
## category는 Bed/Yellow의 형태임
def FindMetaRecommend(df, category):
    result = MetaRecommend.recommend_stuff(df, category)
    return result

## 하나로 합친 함수 (df, 가구타입, 색상타입) 넣으면 반환
def SimpleMetaRecommend(df, FurnitureType, ColorType):
    tmp_dict = ReturnCategory(FurnitureType, ColorType)
    tmp_str = MakeStringCategory(tmp_dict)
    return FindMetaRecommend(df, tmp_str)


## 파일 전송하기
def SendFileToUrl(file):
    upload = {'userfile':file}

    print(file)

    res = requests.post('http://www.mongilmongilgames.com/image/upload.php', files = upload)

    print(res.text)

    print('파일 업로드 결과코드:', res)


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
@cross_origin(origin='*')
def index():
    return '안녕하세요'

# 로그인s
# input : deviceId
# 중간과정 : DB에서 deviceId로 검색해서 결과 없으면 DB에 디바이스 아이디 저장
# DB에서 deviceId로 검색해서 맵 결과 있으면 그 결과 가져오기
# output : 사용자의 배치한 인테리어 배치도
@app.route('/Login', methods=['POST'])
def login():
    print("로그인")
    json_data = request.get_json()
    deviceId = json_data['DeviceId']

    # 가장 최신 데이터 하나만 찾아오기
    result = memberDB.find_one({'DeviceId':deviceId},sort=[('_id', pymongo.DESCENDING)])
    print(result)

    # 신규회원의 경우
    if result == None:
        memberDB.insert_one({'DeviceId':deviceId})
        return MakeResultJson(False)
    # 아이디는 있지만 인테리어 정보가 없는 경우
    elif "Map" not in result:
        return MakeResultJson(False)
    # 아이디도 존재하고 인테리어 정보도 있는 경우
    else:
        return MakeResultJson(True, result['Map'])


# 맵 저장
# input : DeviceId, Map
# output : 성공여부
# 해당 아이디 없으면 insert되고 존재하면 update하는 방식
@app.route('/Save', methods=['POST'])
def Save():
    print("맵저장")
    json_data = request.get_json()
    deviceId = json_data['DeviceId']
    map = json_data['Map']

    print(deviceId)
    print(map)

    memberDB.update({'DeviceId':deviceId},{'DeviceId':deviceId,'Map':map},upsert=True)

    return MakeResultJson(True)


# 실제 가구 추천 (카테고리 / 색상 기반)
# input : FurnitureType, ColorType
# output : productDB에서 검색결과에 맞는 상품 리스트
@app.route('/Recommend', methods=['POST'])
def Recommend():
    print("실제 가구 추천")

    json_data = request.get_json()
    RecommendRequestData = json_data['RecommendRequestData']

    FurnitureType = RecommendRequestData['FurnitureType']
    ColorType = RecommendRequestData['ColorType']

    # 테이블에서 검색해서 결과 가져오기, 최신순
    product_list = list(productDB.find({'Category':FurnitureType, 'Color':ColorType}).sort("_id", -1))

    result_bool = False

    if len(product_list) > 0:

        # 제목이 일치하는 애들끼리 정렬하고 price오름차순으로 가격이 싼 것만 남기고 중복은 제거함
        df = pd.DataFrame(product_list)
        df_sorted = df.sort_values(by=['Title', 'Price'], ascending=True)
        df_drop = df_sorted.drop_duplicates(['Title'],keep='first')

        product_list = df_drop.to_dict('records')
        print(product_list)

        result_bool = True

    # 결과값과 데이터
    data_list = {"Result":result_bool,"Data":product_list}

    # bson -> json 형태로
    result = dumps(data_list, ensure_ascii=False)

    return result


# 가구별로 아무 제품이나 랜덤 추천
# input : 가구 카테고리
# output : productDB의 가구별 상품 하나씩만
@app.route('/RecommendRandom', methods=['POST'])
def RandomRecommend():
    print('랜덤 상품 추천')
    
    cate_list = ['Bed','BookShelf','Chair','Desk','FlowerPot','PhotoFrame','Sofa','Stand']

    random_list = []

    for category in cate_list:
        # Get one random document matching {a: 10} from the mycoll collection.
        random_record = list(productDB.aggregate([{'$match': {'Category': category}},{'$sample': {'size': 1}}]))
        print(random_record)
        # 1개씩 찾아오므로 1개일 때만 리스트에 추가
        if len(random_record) == 1:
            random_list.append(random_record[0])

    result_bool = False

    # DB에 결과 있으면
    if len(random_list) > 0:
        result_bool = True

    # 결과값과 데이터
    data_list = {"Result":result_bool,"Data":random_list}

    # bson -> json 형태로
    result = dumps(data_list, ensure_ascii=False)

    return result


# 유니티에서 가구 선택시 추천 위치 반환
# input : furniture type, color type (str)
# output : Result, pos_x,pos_y 추천 위치
# @app.route('/RecommendPos', methods=['POST'])
# def RecommendPosition():
#     print('추천 위치 반환')
#
#     json_data = request.get_json()
#     PosRequestData = json_data['PosRequestData']
#
#     recom_list = recom_position_unity.load_best_area(PosRequestData['FurnitureType'], PosRequestData['ColorType'])
#
#     print(recom_list)
#
#     result_bool = False
#
#     if len(recom_list) > 0:
#         result_bool = True
#
#     data_list = {"Result": result_bool, "Data": recom_list}
#
#     return data_list


# 가구 위치 반환 최신버전
# input : 가구 타입, 가구 색상, 해당 사용자의 DeviceId
# output : 추천할 가구타입/색상, 해당 가구의 위치정보
@app.route('/RecommendPos', methods=['POST'])
def RecommendPosition():
    print('추천 위치 반환')

    json_data = request.get_json()
    PosRequestData = json_data['PosRequestData']

    deviceId = json_data['DeviceId']

    result = None

    map = memberDB.find_one({'DeviceId': deviceId}, sort=[('_id', pymongo.DESCENDING)])

    # 사용자에게 맵이 있을 경우에만
    if ('Map' in map):
        user_data = json.loads(map['Map'])

        # 추천 가구 위치
        result = new_pos.ReturnRecomFurniture(user_data, PosRequestData['FurnitureType'], PosRequestData['ColorType'])

    # 추천 가구 결과가 하나도 없으면 구역별 빈도수로 구한 값 반환
    if ((result == None) or (len(result) < 1)):
        result = recom_position_unity.load_best_area(PosRequestData['FurnitureType'], PosRequestData['ColorType'])

    print(result)

    result_bool = False

    if len(result) > 0:
        result_bool = True

    data_list = {"Result": result_bool, "Data": result}

    return data_list



## Basket ------------------------------- 장바구니 -------------------------------

## 장바구니 추가
## input : DeviceId, productList
## output : 성공여부
@app.route('/UpdateBasket', methods=['POST'])
def UpdateBasketDB():
    print('장바구니 추가')

    json_data = request.get_json()

    deviceId = json_data['DeviceId']
    productList = json_data['Product']


    print(productList)

    # DeviceId에 장바구니 없으면 생성하고 있으면 update한다
    result = basketDB.update({'DeviceId': deviceId}, {'DeviceId': deviceId, 'ProductList': productList}, upsert=True)

    result_bool = False

    if (len(result) > 0):
        result_bool = True

    Data = {'Result':result_bool}

    return jsonify(Data)


# 장바구니 불러오기
# input : deviceId
# output: 장바구니의 물품 리스트

@app.route('/LoadBasket', methods=['POST'])
def LoadBasketDB():
    print('장바구니 로드')

    json_data = request.get_json()
    deviceId = json_data['DeviceId']

    basket_list = basketDB.find_one({'DeviceId':deviceId})

    result_data = []

    result_bool = False

    # 장바구니가 존재하면
    if (basket_list):
        
        product_list_str = basket_list['ProductList']
        # str형태를 다시 리스트로
        product_list = json.loads(product_list_str)

        tmp_str = '.*'

        if (len(product_list) > 0):
            result_bool = True
            for prod in product_list:
                # productDB의 Link컬럼에서 *아이디 상품 찾아옴
                product_info = productDB.find_one({'Link':{'$regex' : tmp_str+prod}})
                result_data.append(product_info)

    data_list = {"Result":result_bool,"Data":result_data}

    print(data_list)

    # bson -> json 형태로
    result = dumps(data_list, ensure_ascii=False)

    return result


# 장바구니 삭제
# input : deviceId
# output : 성공여부
@app.route('/DeleteBasket', methods=['POST'])
def DeleteBasketDB():
    print('장바구니 삭제')
    
    json_data = request.get_json()
    deviceId = json_data['DeviceId']

    # DB에서 삭제
    result = basketDB.delete_one({'DeviceId':deviceId})

    result_bool = False

    print('삭제된 개수:', result.deleted_count)

    if (result.deleted_count > 0):
        result_bool = True

    result_data = {'Result':result_bool}

    return result_data

## ------------------------------------장바구니 끝 ----------------------------


## 장바구니 상품과 관련된 상품 추천 로드하기
## input : 상품명 (Title)
## output : RelativeDB의 일치하는 상품 리스트
@app.route('/LoadRelative', methods=['POST'])
def LoadRelativeDB():
    print('장바구니와 관련된 상품 리스트 추천')

    json_data = request.get_json()
    relative_data = json_data['relativeRequestData']

    product_name = relative_data['Title']

    # list로 감싸서 가져오기, 문자열이 일치하는 것과 포함하는 경우 둘 다 가져옴, 4개로 제한
    relative_list = list(relativeDB.find({'Relative':{'$regex':product_name}}).limit(4))

    result_bool = False

    # DB에 결과 있으면
    if len(relative_list) > 0:
        result_bool = True

    # 결과값과 데이터
    data_list = {"Result":result_bool,"Data":relative_list}

    # bson -> json 형태로
    result = dumps(data_list, ensure_ascii=False)

    return result


## 메타버스 내의 가구 타입과 색상에 따른 추천
## input : 가구타입, 색상타입 (string)
## output : 추천 가구의 타입,색상조합 리스트와 코사인유사도
@app.route('/MetaRecommendType', methods=['POST'])
def MetaRecommendType():
    print('메타버스 가구 추천')
    json_data = request.get_json()
    relative_data = json_data['MetaRecommendRequestData']

    # string형임
    furniture_type = relative_data['FurnitureType']
    color_type = relative_data['ColorType']
    
    # string -> int형
    fur_index = furlist.index(furniture_type)
    color_index = colorlist.index(color_type)

    ## 코사인 유사도
    recom_df = SimpleMetaRecommend(cosine_df, fur_index, color_index)

    result_bool = False

    result_data = []

    if len(recom_df) > 0:
        result_bool = True

        result_index = recom_df.index.to_list()
        result_value = recom_df.to_list()
        
        # 리스트 2개를 dict로 묶기 (카테고리/색상과 코사인유사도 묶기)
        for index,value in zip(result_index, result_value):
            tmp_dict = {}
            tmp_dict['index'] = index
            tmp_dict['value'] = value
            result_data.append(tmp_dict)

        print(result_data)

        data_list = {"Result": result_bool, "Data": result_data}

    return data_list


## --------------------------- 중고거래 게시판 시작 --------------------------

## 이미지 하나 가져오기 및 이미지 서버에 저장
@app.route('/GetImageClass', methods=['POST'])
def GetImageClass():
    print('이미지 저장하기')
    img_file = request.files['file']
    
    # 로컬에 폴더 생성
    os.makedirs('./upload_images', exist_ok=True)

    file_name = secure_filename(img_file.filename)
    
    # 로컬에 저장
    img_file.save('./upload_images/' + file_name)
    # FileStorage형태로 다시 부르기
    img = open('./upload_images/' + file_name, 'rb')

    # 서버로 파일 저장
    SendFileToUrl(img)

    print(file_name)
    
    # 메모리 누수 막기
    img.close()

    return 'done!'


# 이미지 분류 모델
# input : 이미지 파일
# output : 어떤 가구인지 레이블
@app.route('/ReturnFurnitureClass', methods=['POST'])
def GetFurnitureClass():
    print('이미지로 가구 카테고리 분류하기')
    img_file = request.files['file']

    # 이미지 분류 모델로 예측한 카테고리 반환
    pred = realClassification.predict_img(img_file)

    print(pred)

    result_data = {'Data':pred}

    return result_data


## 게시판 글 등록
# 카테고리, 가구명, 사진, 가격, 게시판 제목, 내용, 등록자id, 게시판 인덱스, 상태
# input : form-data, 이미지파일과 게시글의 정보
# output : 성공여부
# 이미지 파일은 이미지 서버에 따로 저장하고 게시글 DB에 게시글 정보 저장
@app.route('/InsertUsedBoard', methods=['POST'])
def InsertUsed():
    print('중고거래 게시판 글 등록 및 수정')
    # 이미지 파일 받기
    img_file = request.files['file']

    # 파일명
    file_name = secure_filename(img_file.filename)
    # 확장자
    extension = file_name.split('.')[-1]

    # form 데이터 받기
    form_data = request.form.to_dict()

    # 인덱스는 숫자로 저장
    index = 1

    ## 여기는 글 수정
    # 만약 인덱스를 보냈고 그 인덱스 값이 -1보다 크면 글 수정임
    if ('index' in form_data) and (int(form_data['index']) > -1):
        print('글 수정')
        index = int(form_data['index'])
        form_data['index'] = index
    else:
        ## 글 등록
        print('글 등록')
        # 게시글에서 최신 글 가져와서 인덱스 값 추출
        # 글이 하나도 없으면 index는 1임
        results = list(usedDB.find({}).sort("_id", -1))

        ## 테이블에 데이터가 하나라도 있어야 조건에 걸림
        if (len(results) > 0):
            ## 게시판 인덱스는 최근 추가된 데이터의 인덱스 + 1
            index = int(results[0]['index']) + index

        form_data['index'] = index


    # 이미지 파일명 (경로는 폴더명 변경에 유의해 넣지 않음)
    # 그대로 넣으면 찾아오기 힘드니까 index + 확장자명 (ex: 1.jpg)
    tmp_name = str(index) + '.' + extension
    form_data['imgName'] = tmp_name
    
    # 0 : 정상, 1 : 삭제, 2 : 비공개
    form_data['state'] = 0

    print(form_data)

    ## 이미지 저장할 폴더 없으면 생성
    os.makedirs('./upload_images', exist_ok=True)
    
    ## 이미지 파일 저장
    img_file.save('./upload_images/' + tmp_name)

    ## 다시 열고
    img = open('./upload_images/' + tmp_name, 'rb')
    
    # 서버로 파일 저장
    SendFileToUrl(img)

    img.close()

    ## 게시판에 글 등록하기 / 수정하기
    result = usedDB.update({'index': int(index)}, form_data, upsert=True)

    ## 결과값 저장
    result_bool = False

    ## 게시판에 글이 등록 혹은 수정되었으면
    if (len(result) > 0):
        result_bool = True

    result_data = {'Result': result_bool}

    return result_data


## 중고거래 게시판 로드하기
## input : 없음
## output : 게시판 글
@app.route('/LoadUsed', methods=['POST'])
def LoadUsedDB():
    print('중고거래 게시판 로드하기')
    # state가 0인 정상적인 게시글들만 최신순으로 가져오기
    board_list = list(usedDB.find({'state':0}).sort("_id", -1))

    print(board_list)

    result_bool = False

    # 글이 없거나 못 불러오면 False임
    if (board_list):
        result_bool = True

        print(len(board_list))

    data_list = {"Result":result_bool, "Data":board_list}

    # bson -> json 형태로
    result = dumps(data_list, ensure_ascii=False)

    return result


# 중고거래 게시글 삭제 (실제 삭제는 아님, state를 변경해서 state가 0인 목록만 정상임)
# state : 0(정상), 1(삭제), 2(비공개)
# input : 게시글 인덱스
# output : 성공여부
@app.route('/DeleteUsed', methods=['POST'])
def DeleteUsedDB():
    print('중고거래 게시판 삭제')

    json_data = request.get_json()
    # 삭제할 게시글의 인덱스
    index = int(json_data['index'])

    # index로 해당 게시글 하나만
    board = list(usedDB.find_one({'index':index}))

    result_bool = False

    # 결과가 있으면
    if (len(board) > 0):
        # state : 1로 변경함
        usedDB.update_one({'index':index},{'$set':{'state':1}})
        result_bool = True

    result = {'Result':result_bool}

    return result

## --------------------------- 중고거래 게시판 끝 --------------------------




@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

# 스케쥴 설정
#sched = BackgroundScheduler(daemon=True)
# sched_result = sched.add_job(Craw.makeJsonItem, 'cron', week='1-4', day_of_week='0-6', minute='2', 'interval')
#sched.start()
# sched.add_job(job, 'interval', seconds=3, id="test_2")

# 1분마다
#sched_result = sched.add_job(MakeJsonToDB, 'cron', minute='*/1')
# 3시간마다
#sched_result = sched.add_job(MakeJsonToDB, 'cron', hour='*/3')

#MakeJsonToDB()
#FromJsonToDB()

## DB 최신순
# results = list(productDB.find({}).sort("_id",-1))
# for result in results:
#     print(result)

if __name__ == '__main__':
    # serve(app, host="0.0.0.0", port=5000)
    # app.run(debug=True) # host = 127.0.0.1 port = 5000
    app.run(host='0.0.0.0', port='5080', debug=False)
