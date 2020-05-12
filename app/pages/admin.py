from app.db import MONGO
from app.config import MongoConfig, CodeStatus, UserType
from app.util import Util, Auth


class Admin:
    def __init__(self):
        self.User = MongoConfig.User

    async def get_all_users(self):
        findRes = await MONGO(collectionName=self.User).find()
        return Util.format_Resp(data=findRes)

    async def add_user(self, params):
        userName = params.get('userName')
        findRes = await MONGO(collectionName=self.User).find({"userName": userName})
        if findRes:
            return Util.format_Resp(code_type=CodeStatus.UserNameExists, message='user exists')
        nowDate = Util.get_now_time()
        params.update({'createDate': nowDate, "updateDate": nowDate})
        await MONGO(collectionName=self.User).insert_one(params)
        return Util.format_Resp(message="add successfully")

    async def delete_user(self, userName):
        await MONGO(collectionName=self.User).mongo_delete({"userName": userName})
        return Util.format_Resp(message="delete successfully")

    async def modify_user(self):
        pass
