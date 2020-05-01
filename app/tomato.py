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
        self.errorList = []

    async def main(self, imageList):

        tasks = [self.downloadImage(url) for url in imageList]
        await asyncio.gather(*tasks)
        returnData = Util.format_Resp(data=self.uIdList)
        if self.errorList:
            returnData.update({"errorMessage": self.errorList})
        return returnData

    async def downloadImage(self, url):

        nowDate = Util.get_now_time(hms=False)
        dirPath = "{}/{}".format(self.basePath, nowDate)

        if not os.path.exists(dirPath):
            os.mkdir(dirPath)

        try:

            async with app.Session.get(url) as response:
                img = await response.read()
                uId = Util.gen_str_md5_hash(Util.get_now_time(ms=True))
                self.uIdList.append(uId)
                imageName = "{}.png".format(uId)
                async with aiofiles.open("{}/{}".format(dirPath, imageName), mode='wb') as f:
                    await f.write(img)
                    return Util.format_Resp(message="save successfully")
        except:
            self.errorList.append({"url": url, "message": "download failed"})

    async def get_detection_data(self, taskIdList):

        readTasks = [self.read_file(tId) for tId in taskIdList]
        await asyncio.gather(*readTasks)
        return Util.format_Resp(data=self.dataList)

    async def find_data(self, uId):
        finRes = await MONGO(collectionName=MongoConfig.ImageCommitHistory).find({"uId": uId}, length=1)
        if finRes:
            self.fileNameList.append(finRes[0].get("name"))

    async def read_file(self, taskId):
        '''

        :param name: 2020-04-28-4.png
        :return:
        '''
        try:
            async with aiofiles.open("{}/{}.txt".format(self.basePath, taskId), mode='r') as f:
                rList = await f.readlines()
                rList = [r.replace("\n", "").replace(" ", "") for r in rList]
                length, width = rList[1::2]
                self.dataList.append({"taskId": taskId, "result": {"length(pixel)：": length,
                                                                   "width(mm)：": width},
                                      "status": ExecuteStatus.success})
        except:
            self.dataList.append({"taskId": taskId, "result": {"length(pixel)：": "",
                                                               "width(mm)：": ""}, "status": ExecuteStatus.failure})