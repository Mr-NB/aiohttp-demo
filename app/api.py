import asyncio
from aiohttp import web
from app import app
from aiohttp_jinja2 import template, render_template
from app.util import Util
from app.config import CodeStatus
from app.tomato import TomAto

routes = web.RouteTableDef()


@routes.get('/config/get')
async def config_get(request):
    '''
    获取配置信息
    :param request:
    :return:
    '''
    return web.json_response(await app.config.config)


@routes.post('/api/upload')
async def upload(request):
    '''
    获取配置信息
    :param request:
    :return:
    '''
    params = await request.json()
    images = params.get("image")
    if not images:
        return web.json_response(Util.format_Resp(code_type=CodeStatus.NoDataError, message="invalid data"))
    config = await app.config.config
    basePath = config.get("imageFilePath", "/home/nick/project/demo/aiohttp-demo/app/static/images")

    return web.json_response(await TomAto(basePath).main(images))


@routes.post('/api/read')
async def read_detection_data(request):
    '''
    获取配置信息
    :param request:
    :return:
    '''
    params = await request.json()
    uIds = params.get("uIds")
    config = await app.config.config
    basePath = config.get("dataFilePath", "/home/nick/project/demo/aiohttp-demo/app/static/data")
    return web.json_response(await TomAto(basePath).get_detection_data(uIds))
