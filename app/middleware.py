import logging, sys
from aiohttp import web
from app.util import Util, Auth
from app.config import CodeStatus, MongoConfig


@web.middleware
async def request_middleware(request, handler):
    if str(request.content_type) == 'application/json':
        response = await handler(request)
    else:
        multidict = await request.post()
        jsons = {}
        for key in iter(multidict):
            jsons[key] = multidict[key]

        request.json = jsons
        response = await handler(request)
    return response


@web.middleware
async def api_middleware(request, handler):
    ip = request.remote
    from app.db import MONGO
    if request.method == "OPTIONS":
        return await handler(request)

    if request.path.startswith('/static'):
        return await handler(request)
    # auth
    if request.path == "/api/user/login":
        return await handler(request)
    if not request.path.startswith('/api'):
        return await handler(request)
    token = request.headers.get('Authorization')
    if not token:
        return web.json_response(Util.format_Resp(code_type=CodeStatus.Unauthorized, message='Unauthorized'))
    authRes = Auth.decode_auth_token(token)
    if authRes.get('code') != 200:
        errorMessage = authRes.get('message')
        return web.json_response(Util.format_Resp(code_type=CodeStatus.Unauthorized, message=errorMessage))
    tokenData = authRes.get('data')
    userName = tokenData.get('data', {}).get('username', '')
    request['username'] = userName
    mongo = MONGO(collectionName=MongoConfig.IpStatistic)
    filter_condition = {"ip": ip}
    if await mongo.find(filter_condition):
        await mongo.update_one(filter_condition, {'$inc': {'count': 1}, "$set": {"updateDate": Util.get_now_time()}})
    else:
        filter_condition.update({'count': 1, 'userName': userName, "createDate": Util.get_now_time()})
        await mongo.insert_one(filter_condition)
    return await handler(request)


@web.middleware
async def error_middleware(request, handler):
    try:
        response = await handler(request)
        return response
    except web.HTTPException as ex:
        if ex.status == 404:
            res = Util.format_Resp(code_type=CodeStatus.NotFoundError,
                                   alert='page not found')
            return web.json_response(res, status=CodeStatus.NotFoundError.value)
        raise
    except:
        exp = sys.exc_info()
        data = Util.format_Resp(code_type=CodeStatus.UnknownError, exp_obj=exp)
        logging.info(data.get('errorDetail'))
        return web.json_response(data)
