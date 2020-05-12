# About page
import sys
from app.upload import BaseUpload
from app.db import MONGO
from app.config import MongoConfig
from app.util import Util


class Common(BaseUpload):
    name = sys._getframe().f_code.co_name
    uploadCollection = MongoConfig.Common

    @classmethod
    async def get(cls, name=None):
        '''

        :param name: ["x1","x2"]|{}
        :return:
        '''
        if name:
            findRes = await MONGO(collectionName=cls.uploadCollection).find({"name": {"$in": name}})
        else:
            findRes = await MONGO(collectionName=cls.uploadCollection).find()

        return Util.format_Resp(data=findRes)
