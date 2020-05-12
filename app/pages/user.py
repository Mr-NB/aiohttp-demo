from app.db import MONGO
from app.config import MongoConfig, CodeStatus, UserType
from app.util import Util, Auth


class User:
    def __init__(self):
        self.User = MongoConfig.User

    async def login(self, userName, password):
        findRes = await MONGO(collectionName=self.User).find({"userName": userName, "password": password})
        if findRes:
            authRes = await Auth.encode_auth_token(userName)
            if authRes.get('code') != 200:
                return authRes
            token = authRes.get('data')
            role = findRes[0].get('role')
            return Util.format_Resp(message="login successfully",
                                    data={'token': token, 'userName': userName, "role": role})
        else:
            return Util.format_Resp(code_type=CodeStatus.PasswordInvalid, message="login failed")

    async def register(self, userName, password, role=UserType.common):
        findRes = await MONGO(collectionName=self.User).find({"userName": userName})
        if findRes:
            return Util.format_Resp(code_type=CodeStatus.UserNameExists, message="username exists")
        else:
            await MONGO(collectionName=self.User).insert_one(
                {"userName": userName, "password": password, "role": role, "createDate": Util.get_now_time()})
            return Util.format_Resp(message="register successfully")

    async def modify_password(self, userName, oldPassword, newPassword):
        findRes = await MONGO(collectionName=self.User).find({"userName": userName})
        if findRes:
            data = findRes[0]
            password = data.get('password')
            if password != oldPassword:
                return Util.format_Resp(code_type=CodeStatus.PasswordInvalid, message='password is wrong')
            await MONGO(collectionName=self.User).update_one({"userName": userName},
                                                             {"$set": {"password": newPassword,
                                                                       "modifyDate": Util.get_now_time()}})
            return Util.format_Resp(message='modify password successfully')
        else:
            return Util.format_Resp(code_type=CodeStatus.Unauthorized, message='user does not exists')
