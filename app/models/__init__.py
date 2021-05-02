# @Eamil    : iamfuture_x@outlook.com
# @Author  : Mr-NB
import os
from datetime import datetime
from enum import Enum

import aiomysql
from tortoise.models import Model
from tortoise import fields

from app.util import Util
from app.lib import OSS


async def init_mysql(loop=None):
    return await aiomysql.create_pool(host='127.0.0.1', port=3306,
                                      user='root', password='',
                                      db='mysql', loop=loop)


TORTOISE_ORM = {
    "connections": {"default": os.getenv("MYSQL", "mysql://root:@localhost:3306/agro_cloud_doctor")},
    "apps": {
        "models": {
            "models": ["aerich.models", "app.models.model"],
            "default_connection": "default",
        },
    },
}


class BaseModel(Model):
    id = fields.IntField(pk=True)
    gmt_create = fields.DatetimeField(auto_now_add=True)
    gmt_modified = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.id

    @classmethod
    def toDict(cls, obj, delKeys=[]):
        if not obj:
            return {}
        data = {}
        for item in obj._meta.fields:
            if item in delKeys:
                continue
            value = getattr(obj, item)
            if isinstance(value, Enum):
                value = value.value
            elif isinstance(value, datetime):
                if item in ["aim_datetime", "plant_start_datetime"]:
                    value = Util.datetime_to_str(value, "%Y-%m-%d")
                else:
                    value = Util.datetime_to_str(value, "%Y-%m-%d %H:%M")
            elif item in ["snapshot", "company_logo", "seed_photo","company_wx_logo"]:
                if not value:
                    value = []
                else:
                    baseUrl = os.getenv("STATICFILEDOMAIN",
                                        "https://agro-cloud-doctor-pictures.oss-cn-beijing.aliyuncs.com")
                    value = [{"origin": OSS.get_temp_url(pic),
                              "thumbnail": "{}/{}?x-oss-process=image/resize,p_50".format(baseUrl,
                                                                                          pic)} for
                             pic in value.split(",")]

            else:
                value = getattr(obj, item)
            data[item] = value
        return data

    @classmethod
    async def add(cls, data):
        await cls(**data).save()
        return Util.format_Resp(message="添加成功")

    @classmethod
    async def add_all(cls, data):
        for item in data:
            await cls(**item).save()
        return Util.format_Resp(message="添加成功")

    @classmethod
    async def get_one(cls, filterParams=None):
        if filterParams:
            queryObj = await cls.get_or_none(**filterParams)
            if not queryObj:
                data = {}
            else:
                data = cls.toDict(queryObj)
        else:
            data = cls.toDict(await cls.first())
        return Util.format_Resp(data=data)

    @classmethod
    async def get_all(cls, page=None, pageSize=None, filterParams={}):
        filterObj = cls.filter(**filterParams)
        if page and pageSize:
            data = list(
                map(lambda x: cls.toDict(x),
                    await filterObj.offset((int(page) - 1) * int(pageSize)).limit(int(pageSize))))
            return Util.format_Resp(data=data, count=await filterObj.count(), curPage=page)
        else:
            data = [cls.toDict(item) for item in await filterObj.all()]
            return Util.format_Resp(data=data)

    @classmethod
    async def remove(cls, id):
        await cls.filter(id=id).delete()
        return Util.format_Resp(message="删除成功")

    @classmethod
    async def update(cls, data):
        '''
        更新，如果没有传id则为新增
        :param data:
        :return:
        '''
        id = data.get("id")
        if not id:
            return await cls.add(data)
        del data["id"]
        if data.get("start_datetime") and data.get("end_datetime"):
            data["work_hours"] = Util.cal_work_hour(data.get("start_datetime"), data.get("end_datetime"))
        await cls.filter(id=id).update(**data)
        return Util.format_Resp(message="更新成功")
