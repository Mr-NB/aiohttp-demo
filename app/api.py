import os
from aiohttp import web
from app.util import Util
from app.config import CodeStatus
from app.tomato import TomAto
from pathlib import Path

routes = web.RouteTableDef()
staticPath = str(Path(__file__).parent / "static")


@routes.post('/api/create-task')
async def upload(request):
    '''
    获取配置信息
    :param request:
    :return:
    '''
    params = await request.json()
    images = params.get("image")
    if not images:
        return web.json_response(Util.format_Resp(code_type=CodeStatus.NoDataError, message="invalid parameters"))

    basePath = os.getenv("imageFilePath", '{}/images'.format(staticPath))
    if not os.path.exists(basePath):
        os.mkdir(basePath)
    return web.json_response(await TomAto(basePath).main(images))


@routes.post('/api/task-result')
async def read_detection_data(request):
    '''
    获取配置信息
    :param request:
    :return:
    '''
    params = await request.json()
    taskIds = params.get("taskIds")
    if not taskIds:
        returnData = Util.format_Resp(code_type=CodeStatus.ParametersMissError, message="invalid parameters")
    else:

        basePath = os.getenv("dataFilePath", '{}/data'.format(staticPath))
        if not os.path.exists(basePath):
            os.mkdir(basePath)
        returnData = await TomAto(basePath).get_detection_data(taskIds)
    return web.json_response(returnData)
