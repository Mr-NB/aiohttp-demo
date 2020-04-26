import asyncio
from aiohttp import web
from app import app
from aiohttp_jinja2 import template, render_template
from app.pages.about import About
from app.config import MongoConfig
from app.pages.common import Common

from app.xigua import XiGua

routes = web.RouteTableDef()


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


@routes.post('/api/xigua/downloadUrl')
async def parse_xigua_url(request):
    params = await request.json()
    url = params.get("url", "")

    praseRes = await XiGua().praseXigua(url)
    return web.json_response(praseRes)


@routes.get('/api/xigua/commitHistory')
async def get_xigua_commitHistory(request):
    return web.json_response(await XiGua().get_commit_history())


@routes.post('/api/about/upload')
async def about_upload(request):
    params = await request.post()

    res = await About().upload(params)
    return web.json_response(res)


@routes.get('/api/about/get')
async def get_upload(request):
    findRes = await About().get()
    return web.json_response(findRes)


@routes.post('/api/common/upload')
async def common_upload(request):
    params = await request.post()
    res = await Common().upload(params)
    return web.json_response(res)


@routes.get('/api/common/get')
async def get_common(request):
    findRes = await Common().get()
    return web.json_response(findRes)
