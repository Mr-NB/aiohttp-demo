import random
import zlib
from app.lib import Lib


async def praseXigua(url, headers):
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
    return resList
