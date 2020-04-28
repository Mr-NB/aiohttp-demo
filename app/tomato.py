import os, sys
import aiofiles, asyncio
from app import app
from app.util import Util
from app.db import MONGO
from app.config import MongoConfig, CodeStatus, ExecuteStatus


class TomAto:

    def __init__(self, basePath):
        self.startCount = ""
        self.commitId = Util.gen_id()
        self.basePath = basePath
        self.uIdList = []
        self.fileNameList = []
        self.dataList = []

    async def main(self, imageList):
        nowDate = Util.get_now_time(hms=False)
        findRes = await MONGO(collectionName=MongoConfig.ImageCommitHistory).find({"commitDate":
                                                                                       {"$gte": nowDate,
                                                                                        "$lte": Util.get_now_time(
                                                                                            hms=False,
                                                                                            condition={
                                                                                                "days": 1},
                                                                                            is_before=False)}},
                                                                                  length=1, sort=("number", -1))
        if findRes:
            data = findRes[0]
            self.startCount = data.get("number") + 1
        else:
            self.startCount = 0
        tasks = [self.downloadImage(url) for url in imageList]
        await asyncio.gather(*tasks)
        # for url in imageList:
        #     await self.downloadImage(url)
        return Util.format_Resp(data=self.uIdList)

    async def downloadImage(self, url):

        nowDate = Util.get_now_time(hms=False)
        dirPath = "{}/{}".format(self.basePath, nowDate)
        if not os.path.exists(dirPath):
            os.mkdir(dirPath)

        insertData = {"commitId": self.commitId,
                      "commitDate": Util.get_now_time(ms=True), "url": url}
        try:
            async with app.Session.get(url) as response:
                img = await response.read()

                imageName = "{}-{}.png".format(nowDate, self.startCount)
                async with aiofiles.open("{}/{}".format(dirPath, imageName), mode='wb') as f:
                    await f.write(img)
                    uId = Util.gen_str_md5_hash(Util.get_now_time(ms=True))
                    self.uIdList.append(uId)

                    insertData.update(
                        {"number": self.startCount, "name": imageName, "status": ExecuteStatus.success, "uId": uId})

                    await MONGO(collectionName=MongoConfig.ImageCommitHistory).insert_one(insertData
                                                                                          )
                    self.startCount += 1
                    return Util.format_Resp(message="save successfully")
        except:
            exp = sys.exc_info()
            errorMessage = Util.format_Resp(code_type=CodeStatus.UnknownError, exc_obj=exp, sys_obj=sys._getframe(),
                                            message="save failed")
            insertData.update({"errorMessage": errorMessage, "status": ExecuteStatus.failure})
            await MONGO(collectionName=MongoConfig.ImageCommitHistory).insert_one(insertData
                                                                                  )
            return errorMessage

    async def get_detection_data(self, uIdList):
        tasks = [self.find_data(uId) for uId in uIdList]
        await asyncio.gather(*tasks)

        readTasks = [self.read_file(fileName) for fileName in self.fileNameList]
        await asyncio.gather(*readTasks)
        return Util.format_Resp(data=self.dataList)

    async def find_data(self, uId):
        finRes = await MONGO(collectionName=MongoConfig.ImageCommitHistory).find({"uId": uId}, length=1)
        if finRes:
            self.fileNameList.append(finRes[0].get("name"))

    async def read_file(self, name):
        '''

        :param name: 2020-04-28-4.png
        :return:
        '''
        splitList = name.split('.')[0].split('-')
        dirName = '-'.join(splitList[:3])
        fileName = "{}.txt".format("-".join(splitList))
        dirPath = self.basePath + "/{}".format(dirName)
        async with aiofiles.open("{}/{}".format(dirPath, fileName), mode='r') as f:
            rList = await f.readlines()
            res = dict(zip(rList[::2], rList[1::2]))
            self.dataList.append({"fileName": fileName, "data": res})
