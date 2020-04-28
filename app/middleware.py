import logging, sys
from aiohttp import web
from app.util import Util
from app.config import CodeStatus, MongoConfig


@web.middleware
async def api_middleware(request, handler):
    ip = request.remote
    from app.db import MONGO
    mongo = MONGO(collectionName=MongoConfig.IpStatistic)
    filter_condition = {"ip": ip}
    if await mongo.find(filter_condition):
        await mongo.update_one(filter_condition, {'$inc': {'count': 1}})
    else:
        filter_condition.update({'count': 1})
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
