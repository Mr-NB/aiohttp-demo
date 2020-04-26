

# About page
import sys
from app.upload import BaseUpload
from app.db import MONGO
from app.config import MongoConfig
from app.util import Util


class Common(BaseUpload):
    name = sys._getframe().f_code.co_name
    uploadCollection = MongoConfig.Common

    async def get(self):
        findRes = await MONGO(collectionName=self.uploadCollection).find()

        return Util.format_Resp(data=findRes)
