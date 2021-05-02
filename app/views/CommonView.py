# @Eamil    : iamfuture_x@outlook.com
# @Author  : Mr-NB
import os
from datetime import datetime

from tortoise.functions import Count, Sum

from app.models.model import *
from app.lib import Lib, OSS
from app.config import CodeStatus, RoleMapping






async def get_trace_wxcode(request):
    traceCode = request.rel_url.query.get("trace_code")
    url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}".format(
        os.getenv("APPID", "wxec2eade701cb90f1"), os.getenv("APPSECRET", "f5fa756367c1142a5c8a74c7b740fb0b"))
    res = await Lib.Request(endpoint=url)
    access_token = res.get("response", {}).get("access_token", "")
    url = "https://api.weixin.qq.com/wxa/getwxacode?access_token={}".format(access_token)
    res = await Lib.Request(endpoint=url, methods='post',
                            json={"path": "{}?trace_code={}".format(
                                os.getenv("MINIPROGRAMPATH", "pages/tabbar/trace/trace-preview"), traceCode)})
    if res.get("responseStatus") != 200:
        return Util.format_Resp(code_type=CodeStatus.BadRequest, message=res)
    return Util.format_Resp(
        data=Lib.get_abs_path(await OSS.upload(path='trace/{}.{}'.format(traceCode, 'jpeg'), request=request,
                                               content=res.get("response"))))




async def get_stations(token):
    data = (await Lib.Request(endpoint="https://agro-iot.auto-control.com.cn/api/station", token=token)).get("response")
    if data.get("code") != 200:
        return Util.format_Resp(message=data.get("message"))
    else:
        childrens = data.get("data", [{}])[0].get("children", [])
        return Util.format_Resp(data=[{"id": item.get("id"), "name": item.get("name")} for item in childrens])


async def get_works(params):
    trace_id = params.get("trace_id")
    plant_id = params.get("plant_id")
    if trace_id:
        trace = await TraceModel.get_or_none(id=trace_id)
        if not trace:
            return Util.format_Resp(code_type=CodeStatus.BadRequest, message="trace doesn't exists")
        del params['trace_id']
        filterParams = {"isShow": 1, "plant_id": trace.plant_id, "end_datetime__range": [trace.start_datetime,
                                                                                         trace.close_datetime if trace.close_datetime else datetime.now()]}
    else:
        del params['plant_id']
        filterParams = {"plant_id": plant_id, "status__not_in": [WorkStatusMapping.awaiting.value]}

    return await WorkModel.get_all(
        filterParams=filterParams,
        **params)
