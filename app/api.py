from aiohttp import web
from app import app
from app.pages.about import About
from app.pages.common import Common
from app.pages.user import User, UserType
from app.util import Util
from app.pages.vpn import Vpn
from aiohttp_cors import CorsViewMixin
from app.pages.admin import Admin

from app.xigua import XiGua

routes = web.RouteTableDef()


@routes.get('/api/config/get')
async def config_get(request):
    '''
    获取配置信息
    :param request:
    :return:
    '''

    return web.json_response(Util.format_Resp(data=await app.config.config))


@routes.get('/api/test')
async def config_get(request):
    '''
    获取配置信息
    :param request:
    :return:
    '''

    print(request)
    return web.json_response(await app.config.config)


@routes.post('/api/about/upload')
async def about_upload(request):
    params = await request.post()

    res = await About(params, request.get('username')).upload()
    return web.json_response(res)


@routes.post('/api/about/get')
async def get_upload(request):
    params = await request.json()
    findRes = await About.get(params.get('name'))
    return web.json_response(findRes)


@routes.post('/api/common/upload')
async def common_upload(request):
    params = await request.post()

    res = await Common(request.get('username'), params).upload()
    return web.json_response(res)


@routes.post('/api/common/get')
async def get_common(request):
    params = await request.json()

    findRes = await Common.get(params.get('name'))
    return web.json_response(findRes)


# about user

@routes.post('/api/user/login')
async def login(request):
    params = await request.json()
    username = params.get("userName")
    password = params.get('password')
    findRes = await User().login(username, password)
    return web.json_response(findRes)


@routes.post('/api/user/register')
async def register(request):
    params = await request.json()
    username = params.get("userName")
    password = params.get('password')
    role = params.get('role', UserType.common)
    return web.json_response(await User().register(username, password, role))


@routes.post('/api/user/password/modify')
async def modify_password(request):
    params = await request.json()
    username = params.get("userName")
    oldPassword = params.get('oldPassword')
    newPassword = params.get("newPassword")
    return web.json_response(await User().modify_password(username, oldPassword, newPassword))


# about tool

@routes.post('/api/tool/xigua/downloadUrl')
async def parse_xigua_url(request):
    params = await request.json()
    url = params.get("url", "")

    praseRes = await XiGua().praseXigua(url)
    return web.json_response(praseRes)


@routes.get('/api/tool/xigua/commitHistory')
async def get_xigua_commitHistory(request):
    return web.json_response(await XiGua().get_commit_history())


@routes.get('/api/tool/vpn/get')
async def get_vpn(request):
    return web.json_response(await Vpn().get())


@routes.post('/api/tool/vpn/add')
async def add_vpn(request):
    params = await request.json()
    params.update({"userName": request['username']})
    return web.json_response(await Vpn().add(params))


# @routes.post('/api/tool/vpn/delete')
# async def delete_vpn(request):
#     params = await request.json()
#     ip = params.get('ip')
#     return web.json_response(await Vpn().delete(ip))
#
#
# @routes.post('/api/tool/vpn/modify')
# async def modify_vpn(request):
#     params = await request.json()
#     params.update({"userName": request['username']})
#     return web.json_response(await Vpn().modify(params))


class AdminUserView(web.View, CorsViewMixin):
    """
    White list for author
    """

    async def get(self):
        return web.json_response(await Admin().get_all_users())

    async def post(self):
        params = await self.request.json()
        return web.json_response(await Admin().add_user(params))

    async def put(self):
        return web.json_response({"a": 1})

    async def delete(self):
        params = await self.request.json()
        return web.json_response(await Admin().delete_user(params.get('userName')))
