from aiohttp import web
from app import app
from aiohttp_jinja2 import template, render_template

routes = web.RouteTableDef()


@routes.get('/config/get')
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