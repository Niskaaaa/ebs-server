from flask import Flask, request
from flask_restful import Resource, Api
from flask import Flask
import pymongo
from sshtunnel import SSHTunnelForwarder
import config
from bson import ObjectId
from bson import json_util
from flask import request
import json
from WXBizDataCrypt import WXBizDataCrypt
import requests

config.initconfig()
configData=config.configData
print(configData)


server = SSHTunnelForwarder(
  ssh_address_or_host=('81.68.175.29',22),
  ssh_username = configData['ssh_username'],
  ssh_password = configData['ssh_password'],
  remote_bind_address = configData['ssh_address_or_host'])

server.start()
client = pymongo.MongoClient('81.68.175.29',27816)

db = client['bbs']
col_article=db['_article']


app = Flask(__name__)
api = Api(app)

dblist = client.list_database_names()
# dblist = myclient.database_names() 

""" mylist = [
 {
    "authorId" : ObjectId("5fb9185a9bdb9cb413128db5"),
    "authorName":'Niska',
    "catalog" : "share",
    "title" : "111test",
    "content" : "hhhh",
    "time" : "2020-11-18 14:13:00"
}, {
    "authorId" : ObjectId("5fb9185a9bdb9cb413128db5"),
    "authorName":'Niska',
    "catalog" : "share",
    "title" : "11411test",
    "content" : "hhhh",
    "time" : "2020-11-18 14:13:00"
}, {
    "authorId" : ObjectId("5fb9185a9bdb9cb413128db5"),
    "authorName":'Niska',
    "catalog" : "share",
    "title" : "1411test",
    "content" : "hhhh",
    "time" : "2020-11-18 14:13:00"
}, {
    "authorId" : ObjectId("5fb9185a9bdb9cb413128db5"),
    "authorName":'Niska',
    "catalog" : "share",
    "title" : "1112test",
    "content" : "hhhh",
    "time" : "2020-11-18 14:13:00"
}
]

x = db['_article'].insert_many(mylist)  
# 输出插入的所有文档对应的 _id 值
print(db['_article'].inserted_ids)
article = db['_article'].find()
for x in article:
    print(x)   """

@app.route('/adp/newitem/' , methods=['GET', 'POST'])
def nextitem():
    return {"hhh":"test"}

@app.route('/public/list' , methods=['GET'])
def articleAllList():

    article = db['_article'].find()
    arList = []
    for x in article:
        x['_id']=json_util.dumps(str(x['_id']))
        print(x['_id'])
        arList.append(x)
        
    return json_util.dumps(arList)

@app.route('/public/list<catalog>' , methods=['GET'])
def articleList(catalog):

    article = db['_article'].find({'catalog':catalog})
    arList = []
    for x in article:
        x['_id']=json_util.dumps(str(x['_id']))
        print(x['_id'])
        arList.append(x)
        
    return json_util.dumps(arList)

@app.route('/public/content/<id>' , methods=['GET'])
def articleDetail(id):

    article = db['_article'].find_one({'_id':ObjectId(id)})
    print(article)

        
    return json_util.dumps(article)


@app.route('/login/wxLogin' , methods=['POST'])
def login():
    code=request.get_data()
    data = json.loads(code)
    code=json.loads(code)["code"]
    print(data)
    r= requests.get('https://api.weixin.qq.com/sns/jscode2session?appid='+configData['appid']+'&secret='+configData['appSecret']+'&js_code='+code+'&grant_type=authorization_code')
    r = json.loads(r.text)
    print(r)
    sessionKey=r['session_key']

    encryptedData=data['user']['encryptedData']
    iv=data['user']['iv']

    pc = WXBizDataCrypt(configData['appid'], sessionKey)
    decode = pc.decrypt(encryptedData, iv)
    print(decode)

    exist= db['_user'].find_one({'_openId':decode['openId']})
    if(exist==None):
        createUser(decode['openId'],decode['nickName'])
        exist= db['_user'].find_one({'_openId':decode['openId']})
    print(exist)
    return {"code":200,"name":exist['_name'],"token":exist['_openId']+r['session_key']}

def createUser(openId,name):
    db['_user'].insert_one({'_openId':openId,'_name':name})
    print('created!')


def access_get():
    r= requests.get('https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid='+configData['appid']+'&secret='+configData['appSecret'])
    r = json.loads(r.text)
    print(r)
    return r


@app.route('/postArticle' , methods=['POST'])
def postArticle():
    accessToken = access_get()['access_token']

    data=request.get_data()
    data=json.loads(data)
    postData='{ '+'"content":'+'"'+data['content']+'"'+' }'
    print(postData)
    r= requests.post('https://api.weixin.qq.com/wxa/msg_sec_check?access_token='+accessToken,postData)
    print(r.json())
    return data

if __name__ == '__main__':
    app.run(host='127.0.0.1',port=5000)

