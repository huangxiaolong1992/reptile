from flask import Flask, jsonify, Response
from pymongo import MongoClient
import time

app = Flask(__name__)

from reptile import baiduReplite, xhReplite

'''
设置静态图片
'''
@app.route('/images/<images>')
def images(images):
    with open("./images/"+images, 'rb') as f:
        image = f.read()
        resp = Response(image, mimetype="image/jpeg")
        return resp

'''
 连接数据库 mongodb
'''
conn = MongoClient('mongodb://localhost:27017/')
db = conn.reptilesDB
reptilesDB = db.reptilesDB





'''
    timeTest: 定时任务
    getIp:本机ip
    baiduReplite ： 百度数据
    xhReplite： 星火公司数据
'''


def timeTest(time):
    baiduReplite(reptilesDB, time)
    xhReplite(reptilesDB)


if __name__ == '__main__':
    while True:
        timeTest(time)
        time.sleep(60)
    app.run(host='0.0.0.0', port=80)






