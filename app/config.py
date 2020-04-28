import os, sys
from enum import Enum
from motor.motor_asyncio import AsyncIOMotorClient


class ExecuteStatus:
    failure = 'failure'
    success = 'success'
    ignored = 'ignored'
    executing = 'executing'


class MongoConfig:
    MongoHost = str(os.environ.get('MONGO_HOST', '127.0.0.1'))
    MongoPort = int(os.environ.get('MONGO_PORT', 27017))
    MongoDB = str(os.environ.get('MONGO_DATABASE', "tomato"))
    MONGODB_POOL_SIZE = int(os.environ.get('MAXPOOLSIZE', 100))
    MongoClient = AsyncIOMotorClient(MongoHost, MongoPort)
    CrawlLog = 'crawl_log'
    MonitorLog = 'monitor_log'
    IpStatistic = 'IpStatistic'
    ImageCommitHistory = "ImageCommitHistory"


class IssueType(Enum):
    Timeout = 0
    RedirectToHomepage = 1
    ErrorPage = 2
    NotFoundPage = 404


class CodeStatus(Enum):
    SuccessCode = 200
    LogoWordsError = 208
    Unauthorized = 401
    NotFoundError = 404
    RequestError = 400
    UnknownError = 500
    TimeoutError = 504
    NoDataError = 152
    CmsApiError = 153
    CmsUndoPublishError = 156
    PermissionDenied = 104
    FormatError = 105
    ParametersMissError = 106
    ParametersTypeError = 107
    InvalidDataError = 108
    DataDuplicateError = 109
    SqlError = 110
    SendMailError = 111
    JobRunError = 112
    CmsApiFormatError = 157


class BaseConfig:
    pass


class Local(BaseConfig):
    name = sys._getframe().f_code.co_name

    @property
    async def config(self):
        res = await MongoConfig.MongoClient[MongoConfig.MongoDB].DynamicConfig.find_one({"env": self.name}, {"_id": 0})
        return res


class Pro(BaseConfig):
    name = sys._getframe().f_code.co_name

    @property
    async def config(self):
        res = await MongoConfig.MongoClient[MongoConfig.MongoDB].DynamicConfig.find_one({"env": self.name}, {"_id": 0})
        return res


class Dev(BaseConfig):
    name = sys._getframe().f_code.co_name

    @property
    async def config(self):
        res = await MongoConfig.MongoClient[MongoConfig.MongoDB].DynamicConfig.find_one({"env": self.name}, {"_id": 0})
        return res
