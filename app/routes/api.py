# @Eamil    : iamfuture_x@outlook.com
# @Author  : Mr-NB
from aiohttp import web

from app import app
from app.models.model import *
from aiohttp_swagger3 import SwaggerDocs, SwaggerUiSettings

from app.lib import Util, Lib, OSS
from app.views import CommonView
from app.config import RoleMapping

api_routes = web.RouteTableDef()


@api_routes.get('/test')
async def config_get(request):
    '''
    获取配置信息
    :param request:
    :return:
    '''
    return web.json_response(await app.config.config)


@api_routes.view('/work')
class WorkAPI(web.View):
    def __init__(self, request):
        super(WorkAPI, self).__init__(request)

    async def get(self):
        params = dict(self.request.rel_url.query)
        filterParams = {"status__in": [WorkStatusMapping.success.value, WorkStatusMapping.failed.value],
                        "customer_id": self.request.customerId}
        if self.request.roles == RoleMapping.worker.value:
            filterParams.update({"operator_id": self.request.id})
        params['filterParams'] = filterParams
        return web.json_response(await WorkModel.get_all(**params))

    async def post(self):
        data = await self.request.json()
        data['customer_id'] = self.request.customerId
        return web.json_response(await CommonView.add_work(data, self.request))

    async def put(self):
        data = await self.request.json()
        data['customer_id'] = self.request.customerId
        if self.request.roles == RoleMapping.worker.value:
            data['status'] = WorkStatusMapping.pending
        return web.json_response(await WorkModel.update(data))

    async def delete(self):
        params = self.request.rel_url.query
        return web.json_response(await WorkModel.remove(params.get("id")))
