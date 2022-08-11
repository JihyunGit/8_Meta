from flask import Flask, render_template, request, jsonify
import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


print(pymongo.__version__)
# DB 불러오기
client = pymongo.MongoClient("mongodb+srv://metaverse123:hongil123@accidentlyunity.ts7ta4j.mongodb.net/?retryWrites=true&w=majority", server_api=ServerApi('1'))
db = client.test
# memberDB 없으면 생성하고 있으면 불러옴, 그냥 table임
memberDB = db.members
print("DB 연동 완료")


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

app = Flask(__name__)

@app.route('/')
def index():
    return '안녕하세요'

# 로그인
# input : deviceId
# 중간과정 : DB에서 deviceId로 검색해서 결과 없으면 DB에 디바이스 아이디 저장
# DB에서 deviceId로 검색해서 맵 결과 있으면 그 결과 가져오기
# output : 사용자의 배치한 인테리어 배치도
@app.route('/Login', methods=['POST'])
def login():
    print("login")
    json_data = request.get_json()
    deviceId = json_data['DeviceId']

    result = memberDB.find_one({'DeviceId':deviceId})
    print(result)

    # 신규회원의 경우
    if result == None:
        memberDB.insert_one({'DeviceId':deviceId})
        return MakeResultJson(False)
    # 아이디는 있지만 인테리어 정보가 없는 경우
    elif result['Map'] == None:
        return MakeResultJson(False)
    # 아이디도 존재하고 인테리어 정보도 있는 경우
    else:
        return MakeResultJson(True, result['Map'])

# 해당 아이디 없으면 insert되고 있으면 update하는 방식
# 성공시 True 값 반환
@app.route('/Save', methods=['POST'])
def Save():
    print("save")
    json_data = request.get_json()
    deviceId = json_data['DeviceId']
    map = json_data['Map']

    memberDB.update({'DeviceId':deviceId},{'DeviceId':deviceId,'Map':map},upsert=True)

    return MakeResultJson(True)


# csv를 받아서 DB에 저장하고
# 저장된 DB에서 색상, 카테고리에 속하는 아이템들 불러오고
# 그 정보를 json형태로 리턴
@app.route('/Recommend', methods=['POST'])
def Recommend():
    print("Recommend")

    json_data = request.get_json()
    RecommendRequestData = json_data['RecommendRequestData']
    Index = RecommendRequestData['Index']
    FurnitureType = RecommendRequestData['FurnitureType']
    ColorType = RecommendRequestData['ColorType']

    """
    DB 혹은 CSV 파일에서 찾는 로직
    """

    """
    일단은 가데이터
    """

    RecommendResponseDataList = []
    RecommendResponseDataList.append(MakeRecommendResponseDataJson("https://img.freepik.com/free-photo/white-wall-living-room-have-sofa-and-decoration-3d-rendering_41470-3282.jpg", "쇼파1", "https://www.naver.com"))
    RecommendResponseDataList.append(MakeRecommendResponseDataJson("https://img.freepik.com/free-photo/white-wall-living-room-have-sofa-and-decoration-3d-rendering_41470-3282.jpg", "쇼파2", "https://www.naver.com"))
    RecommendResponseDataList.append(MakeRecommendResponseDataJson("https://img.freepik.com/free-photo/white-wall-living-room-have-sofa-and-decoration-3d-rendering_41470-3282.jpg", "쇼파3", "https://www.naver.com"))

    dic = {
        "Result": True,
        "Data": RecommendResponseDataList
    }

    print(Index, FurnitureType, ColorType)

    return jsonify(dic)

if __name__ == '__main__':
    # serve(app, host="0.0.0.0", port=5000)
    # app.run(debug=True) # host = 127.0.0.1 port = 5000
    app.run(host='0.0.0.0', port='5080', debug=True)
# debug=True이므로 코드 수정 중에도 알아서 다시 시작해줌
































