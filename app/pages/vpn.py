from app.db import MONGO
from app.config import MongoConfig, CodeStatus, UserType
from app.util import Util


class Vpn:
    def __init__(self):
        self.Vpn = MongoConfig.Vpn

    async def get(self):
        findRes = await MONGO(collectionName=self.Vpn).find()

        return Util.format_Resp(data=findRes)

    async def add(self, params):
        ip = params.get('ip')
        params.update({'createDate': Util.get_now_time(), "updateDate": Util.get_now_time()})
        findRes = await MONGO(collectionName=self.Vpn).find({"ip": ip})
        if findRes:
            return Util.format_Resp(code_type=CodeStatus.dataDuplication, message="ip exists")
        else:
            await MONGO(collectionName=self.Vpn).insert_one(
                params)
            return Util.format_Resp(message="add vpn successfully")

    async def modify(self, params):
        ip = params.get('ip')
        params.update({"updateDate": Util.get_now_time()})
        await MONGO(collectionName=self.Vpn).update_one({"ip": ip}, {"$set": params})
        return Util.format_Resp(message="update vpn successfully")

    async def delete(self, ip):

        await MONGO(collectionName=self.Vpn).mongo_delete({"ip": ip})
        return Util.format_Resp(message="delete vpn successfully")
