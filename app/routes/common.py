# @Eamil    : iamfuture_x@outlook.com
# @Author  : Mr-NB

from aiohttp import web

from app import app
from app.views import CommonView
from app.util import Util

app_routes = web.RouteTableDef()


@app_routes.get('/view_trace')
async def view_trace_info(request):
    '''
    获取配置信息
    :param request:
    :return:
    '''

    return web.json_response(await CommonView.get_trace_view_info(dict(request.rel_url.query)))
