# About page
import sys
from app.upload import BaseUpload
from app.db import MONGO
from app.config import MongoConfig
from app.util import Util


class About(BaseUpload):
    name = sys._getframe().f_code.co_name
    uploadCollection = MongoConfig.AboutMe

    async def get(self):
        findRes = await MONGO(collectionName=self.uploadCollection).find()

        return Util.format_Resp(data=findRes)
