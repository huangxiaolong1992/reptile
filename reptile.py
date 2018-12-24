from pyquery import PyQuery as pq
import requests
from urllib import parse
import socket
import os
import time
import json

headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3423.2 Safari/537.36'
}
''' 
     爬取百度新闻
     :keyword 公安部
     :type 1 
     :return 
'''

def baiduReplite(reptiles, time):
    imgArr = []
    baiduWord = "公安部"
    baiduUrl = "https://www.baidu.com/s?tn=news&rtt=4&bsst=1&cl=2&wd=" + parse.quote(baiduWord)
    try:
        html = requests.get(url=baiduUrl, headers=headers)
        print("------------------------请求百度新闻成功-----------------------------")
    except BaseException as f:
        print("%s 连接百度新闻超时" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), f)
        return

    html = html.text
    doc = pq(html)

    items = doc("#content_left").items()
    for item in items:
        if reptiles.count({"type": 1}) == 0:
            for i in range(9, -1, -1):
                title = item.find(".result").eq(i).find('.c-title').text()
                item.find(".result").eq(i).find(".c-summary").find("p").remove()
                item.find(".result").eq(i).find(".c-summary").find("span").remove()
                synopsis = item.find(".result").eq(i).find(".c-summary").text()
                originAddress = item.find(".result").eq(i).find(".c-title").children("a").attr("href")
                imgUrl = item.find(".result").eq(i).find(".c_photo").children("img").attr("src")
                imgArr.append({
                    "title": title,
                    "synopsis": synopsis,
                    "originAddress": originAddress,
                    "imgUrl": imgUrl,
                    "type": 1
                })
        else:
            title = item.find(".result").eq(0).find('.c-title').text()
            item.find(".result").eq(0).find(".c-summary").find("p").remove()
            item.find(".result").eq(0).find(".c-summary").find("span").remove()
            synopsis = item.find(".result").eq(0).find(".c-summary").text()
            originAddress = item.find(".result").eq(0).find(".c-title").children("a").attr("href")
            imgUrl = item.find(".result").eq(0).find(".c_photo").children("img").attr("src")
            if reptiles.find_one({"title": title, "type": 1}) == None:
                imgArr.append({
                    "title": title,
                    "synopsis": synopsis,
                    "originAddress": originAddress,
                    "imgUrl": imgUrl,
                    "type": 1
                })

        for i, data in enumerate(imgArr):
            newImgUrl = request_download(data['imgUrl'], i)
            originAddress = data['originAddress']
            reptiles.insert_one({
                "title": data['title'],
                "synopsis": data['synopsis'],
                "originAddress": originAddress,
                "time": time.strftime("%Y-%m-%d", time.localtime()),
                "imgUrl": newImgUrl,
                "type": 1
            })


'''
   爬取星火官网
   :type:2
   :return
'''


def xhReplite(reptiles):
    '''
      dataArr:图片，标题，内容
    '''

    dataArr = []
    xhUrl = "http://www.szxhdz.com/Info/InfoList.aspx?&catalogID=64&page=1"
    try:
        html = requests.get(url=xhUrl, headers=headers, timeout=1)
        print("------------------------请求星火新闻成功-----------------------------")
    except BaseException as f:
        print("%s 请求星火公司官网超时" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), f)
        return
    html = html.text
    doc = pq(html)
    items = doc(".news").items()
    for item in items:
        if reptiles.count({"type": 2}) == 0:
            for i in range(9, -1, -1):
                title = item.find('li').eq(i).find('a').text()
                synopsis = item.find('li').eq(i).find("span").eq(0).text()
                imgUrl = item.find('li').eq(i).find('img').attr("src")
                originAddress = item.find('li').eq(i).find("a").attr("href")
                dataArr.append({"title": title, "synopsis": synopsis, "imgUrl": imgUrl, "originAddress":originAddress})
        else:
            title = item.find('li').eq(0).find('a').text()
            synopsis = item.find('li').eq(0).find("span").eq(0).text()
            imgUrl = item.find('li').eq(0).find('img').attr("src")
            originAddress = item.find('li').eq(0).find("a").attr("href")
            if reptiles.find_one({"title": title, "type": 2}) == None:
               dataArr.append({"title": title, "synopsis": synopsis, "imgUrl": imgUrl, "originAddress": originAddress})

    for i, data in enumerate(dataArr):
        newImgUrl = request_download("http://www.szxhdz.com" + data['imgUrl'], i)
        originAddress = "http://www.szxhdz.com" + data['originAddress']

        article = newAddress(originAddress)

        reptiles.insert_one({
             "title": data['title'],
             "synopsis": data['synopsis'],
             "originAddress": originAddress,
             "article": article[0],
             "time": time.strftime("%Y-%m-%d", time.localtime()),
             "imgUrl": newImgUrl,
             "type": 2
        })




'''
  爬取文章详情页
  :param  http://www.szxhdz.com 星火官网
  :articleImgArr 图片数组
'''
def newAddress(httpUrl):
    articleImgArr = []
    html = requests.get(url=httpUrl, headers=headers).text
    doc = pq(html)

    if httpUrl.find("http://www.szxhdz.com") != -1:
        items = doc(".article").items()
        for item in items:
            html = item.find(".content").html()
            articleImgLength = len(item.find(".content").find("img"))
            for i in range(0, articleImgLength):
                 newI= request_download("http://www.szxhdz.com" + item.find("img").eq(i).attr("src"), i)
                 articleImgArr.append(newI)
                 html = html.replace(item.find("img").eq(i).attr("src"), articleImgArr[i])
            time = item.find(".title").children("span").text()
            return html, time, newI
    else:
        pass


'''
  下载图片
  imgUrl:抓取到的图片地址
  i:数量
  fastdfsUrl：文件服务器
'''

fastdfsUrl = "http://61.144.226.134:8000/ga/xinghuo-apaas-fastdfsservice/fastdfsservice/fastdfs/singleUploadFile"
def request_download(imgUrl, i):
    #如果图片不存在，直接返回None，否则进行下载，并进行上传到文件服务上
    if imgUrl == None:
        return None

    headers = {
        "requestType": "zuul"
    }

    try:
        path = './images/'
        folder = os.path.exists(path)
        try:
           pic = requests.get(imgUrl, timeout=1)
        except BaseException as f:
            print("请求图片地址失败", f)
            return
        if not folder:
            os.makedirs(path)
        # timeout 超时时间
        string = path + str(i + 1) + '.jpg'
        with open(string, 'wb') as f:
            f.write(pic.content)
            print('----------------------成功下载第%s张图片: %s------------------------------' % (str(i + 1), str(imgUrl)))
            files = {'fileList': open(string, 'rb')}
            res = requests.post(url=fastdfsUrl, headers=headers, files=files)

            if res.status_code == 200:
               if eval((res.text))["code"] == 200:
                   return (eval((res.text))["data"])["fullPath"]
               else:
                   print("----------------------上传fastdfs失败----------------")
            else:
                print("----------------------请求fastdfs失败----------------")

    except Exception as e:
        print('下载第%s张图片时失败: %s' % (str(i + 1), str(imgUrl)))
        # os.remove(string)




