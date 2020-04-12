import requests
import json
import random
import zlib

def praseXigua(url):
    rand_num = str(random.randint(100000000,999999999))
    pc_headers = {'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
    'cookie': 'wafid=c4688220-7c1a-44c1-b014-0136d375dffe; wafid.sig=OgaVjM8xXg1910_pXhxNZWrgLbw; ttwid=6814367997009937934; ttwid.sig=D4on14TrbpzU9R4nmyG7-k79Z7g; xiguavideopcwebid=6814367997009937934; xiguavideopcwebid.sig=vaoI4_VB_nih5FWKHPmrB-dPjzg; ixigua-a-s=0; SLARDAR_WEB_ID=e95377fd-9211-4ba5-ba04-aa3b8eaf352a; _ga=GA1.2.2029572209.1586593690; _gid=GA1.2.1962028532.1586593690; s_v_web_id=k8vo6ma7_HKQ0gpIr_GldT_4TSb_BYun_LRoJ94FMTm4m; RT="z=1&dm=ixigua.com&si=9ngotwi22t&ss=k8wk8jli&sl=0&tt=0"; _gat_gtag_UA_138710293_1=1'}
    # 今日头条App分享来源处理
    if "toutiaoimg.cn" in url:
        itemId= url.split('/')[4]
        url = 'https://www.ixigua.com/i' + itemId+ '/'
    # 西瓜视频App分享来源处理
    if "m.ixigua.com" in url:
        itemId= url.split('/')[4]
        url = 'https://www.ixigua.com/i' + itemId+ '/'
    responseHtml = requests.get(url, headers=pc_headers, allow_redirects=True).content.decode('UTF-8')
    # 获取vid
    vid = responseHtml.split('"vid":"')[1].split('","')[0]
    # 生成签名
    parseUrl = "/video/urls/v/1/toutiao/mp4/" + vid + "?r=" + rand_num
    crc_code = str(zlib.crc32(parseUrl.encode('utf8')))
    # 请求接口
    mResponse = requests.get("http://i.snssdk.com" + parseUrl + "&nobase64=true&s=" + crc_code, headers=pc_headers).content.decode('UTF-8')
    mJson = json.loads(mResponse)
    vedioDict = mJson['data']['video_list']
    return [value for _,value in vedioDict.items()][-1]["main_url"]

print(praseXigua("https://www.ixigua.com/i6807187564584239629/?logTag=hFmq2w-_lLSD0tmCO5KNw"))