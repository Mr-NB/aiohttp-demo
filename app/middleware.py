import logging, sys
from aiohttp import web
from app.util import Util
from app.config import CodeStatus
from app.lib import Lib


@web.middleware
async def api_middleware(request, handler):
    '''
    :param request:
    :param handler:
    :return:
    '''
    from app import app

    ip = request.remote
    if "docs" in request.path:
        return await handler(request)

    headers = request.headers
    token = headers.get("Authorization",
                        "Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiI1NSIsImN1c3RvbWVySWQiOiIxNTkyMDY1MjE0IiwidXNlcm5hbWUiOiLpooTnoJTmuKnlrqQiLCJhdXRob3JpdGllcyI6IiIsImV4cCI6MTYwODExMDY0MH0.K2wbpHLx9InscxERKD8qvFynVJoiXLDaORmX6GB0reCXL8Nirxi1NZeSvskm74IlT4NpoUPRkvKwP10vRwECwQ")
    # config = await app.redis.hkeys(token)
    # if not config:
    data = (await Lib.Request(headers={"Authorization": "Bearer {}".format(token)},
                              endpoint="https://agro-iot.auto-control.com.cn/api/user")).get("response", {}).get(
        "data", {})
    if data:
        del data['createDate']
        del data['modifiedDate']
        del data['active']
        await app.redis.hmset_dict(
            token, data)
    else:
        return web.json_response(Util.format_Resp(code_type=CodeStatus.BadRequest, message="登陆失败"))
    # else:
    #     data = await app.redis.hgetall(token, encoding="utf-8")
    '''
     data中字段
     "id": 6,
    "customerId": 1586272542,
    "createDate": "2020-04-08 07:15:42",
    "modifiedDate": "2020-12-17 01:27:04",
    "phoneNumber": "13911682107",
    "username": "xxf",
    "nickname": "奥托测试",
    "avatar": "",
    "password": "",
    "roles": "ADMIN",
    "active": true
    '''
    for k, v in data.items():
        setattr(request, k, v)
    request.token = token
    return await handler(request)


@web.middleware
async def error_middleware(request, handler):
    try:
        response = await handler(request)
        return response
    except web.HTTPException as ex:
        if ex.status == 404:
            res = Util.format_Resp(code_type=CodeStatus.NotFound,
                                   alert='page not found')
            return web.json_response(res, status=CodeStatus.NotFound.value)
        raise
    except:
        exp = sys.exc_info()
        data = Util.format_Resp(code_type=CodeStatus.UnknownError, exp_obj=exp)
        logging.error(data.get('errorDetail'))
        return web.json_response(data)
