import asyncio
from aiohttp import web
from app import app
from aiohttp_jinja2 import template, render_template
from fake_useragent import UserAgent
from app.lib import Lib
from pyppeteer import launch
from app.xigua import praseXigua

routes = web.RouteTableDef()
ua = UserAgent()


@routes.get('/api/config/get')
async def config_get(request):
    '''
    获取配置信息
    :param request:
    :return:
    '''
    return web.json_response(await app.config.config)


@routes.get('/api/test')
async def config_get(request):
    '''
    获取配置信息
    :param request:
    :return:
    '''

    print(request)
    return web.json_response(await app.config.config)


@routes.post('/api/xigua')
async def parse_xigua_url(request):
    config = await app.config.config
    userAgent = ua.chrome
    params = await request.json()
    url = params.get("url", "")
    awitTime = config.get("xigua", {}).get("awaitTime", 5)
    print(awitTime)
    browser = await launch({'args': ['--no-sandbox', '--disable-setuid-sandbox']})

    page = await browser.newPage()
    await page.goto(url)
    await asyncio.sleep(awitTime)
    cookies = await page.cookies()
    real_url = page.url  # 获取当前URL

    await browser.close()
    cookie = ";".join(["{}={}".format(item.get("name", ""), item.get("value", "")) for item in cookies])
    headers = {"user-agent": userAgent, "cookie": cookie}
    praseRes = await praseXigua(url, headers)
    return web.json_response(praseRes)
