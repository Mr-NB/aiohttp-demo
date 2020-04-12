import random
import zlib
import asyncio
from app import app
from app.lib import Lib
from app.db import MONGO
from app.config import MongoConfig
from app.lib import Util
from app.lib import Lib
from pyppeteer import launch
from fake_useragent import UserAgent
from bs4 import BeautifulSoup


class XiGua:
    def __init__(self):

        self.commitHistoryCollection = MongoConfig.XiGuaCommitHistory
        self.ua = UserAgent()

    async def praseXigua(self, url):
        config = await app.config.config
        userAgent = self.ua.chrome
        awitTime = config.get("xigua", {}).get("awaitTime", 5)
        browser = await launch({'args': ['--no-sandbox', '--disable-setuid-sandbox']})

        page = await browser.newPage()
        await page.goto(url)
        await asyncio.sleep(awitTime)
        cookies = await page.cookies()
        real_url = page.url  # 获取当前URL

        await browser.close()
        cookie = ";".join(["{}={}".format(item.get("name", ""), item.get("value", "")) for item in cookies])
        headers = {"user-agent": userAgent, "cookie": cookie}

        commitId = Util.gen_id()
        rand_num = str(random.randint(100000000, 999999999))

        if "toutiaoimg.cn" in url:
            itemId = url.split('/')[4]
            url = 'https://www.ixigua.com/i' + itemId + '/'
        # 西瓜视频App分享来源处理
        if "m.ixigua.com" in url:
            itemId = url.split('/')[4]
            url = 'https://www.ixigua.com/i' + itemId + '/'
        res = await Lib.Request(headers, url, "get")
        responseHtml = res.get("response")

        bs = BeautifulSoup(responseHtml, "html.parser")
        try:
            title = bs.h1.string
        except:
            title = ""
        # 获取vid
        vid = responseHtml.split('"vid":"')[1].split('","')[0]
        # 生成签名
        parseUrl = "/video/urls/v/1/toutiao/mp4/" + vid + "?r=" + rand_num
        crc_code = str(zlib.crc32(parseUrl.encode('utf8')))
        # 请求接口
        mRes = await Lib.Request(headers, "http://i.snssdk.com" + parseUrl + "&nobase64=true&s=" + crc_code, "get")
        mResponse = mRes.get("response")

        vedioDict = mResponse['data']['video_list']
        resList = []
        for key, value in vedioDict.items():
            definition = value.get("definition", "")
            playUrl = value.get("main_url", "")
            resList.append({"definition": definition, "url": playUrl})
        await MONGO(collectionName=self.commitHistoryCollection).insert_one(
            {"commitId": commitId, "userName": "", "playUrl": resList, "createDate": Util.get_now_time(),
             "title": title})
        return Util.format_Resp(data=resList)

    async def get_commit_history(self):
        findRes = await MONGO(collectionName=self.commitHistoryCollection).find()
        return Util.format_Resp(data=findRes)
