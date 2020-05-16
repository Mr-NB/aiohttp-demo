import os, sys
from enum import Enum
from motor.motor_asyncio import AsyncIOMotorClient


class MongoConfig:
    MongoHost = str(os.environ.get('MONGO_HOST', '127.0.0.1'))
    MongoPort = int(os.environ.get('MONGO_PORT', 27017))
    MongoDB = str(os.environ.get('MONGO_DATABASE', "test"))
    MONGODB_POOL_SIZE = int(os.environ.get('MAXPOOLSIZE', 100))
    MongoClient = AsyncIOMotorClient(MongoHost, MongoPort)
    CrawlLog = 'crawl_log'
    MonitorLog = 'monitor_log'
    IpStatistic = 'IpStatistic'
    XiGuaCommitHistory = "XiGuaCommitHistory"
    AboutMe = "AboutMe"
    Common = "Common"
    User = "User"
    Vpn = "Vpn"


class UserType:
    admin = 1
    common = 2


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

    # 10x about user
    UserNameExists = 100
    UserNameNotExists = 101
    UserNameFormatInvalid = 102
    PasswordFormatInvalid = 103
    PasswordInvalid = 104

    # 11x- about system
    PermissionDenied = 110
    FormatError = 111
    ParametersMissError = 112
    ParametersTypeError = 113
    InvalidDataError = 114
    DataDuplicateError = 115
    SqlError = 116
    SendMailError = 117
    JobRunError = 118
    dataDuplication = 119


class BaseConfig:
    name = sys._getframe().f_code.co_name
    movie = "mp4"
    image = "png"
    excel = "xlsx"

    @property
    async def config(self):
        res = await MongoConfig.MongoClient[MongoConfig.MongoDB].DynamicConfig.find_one({"env": self.name}, {"_id": 0})
        if not res:
            res = {}
        return res


class Local(BaseConfig):
    name = sys._getframe().f_code.co_name


class Pro(BaseConfig):
    name = sys._getframe().f_code.co_name


class Dev(BaseConfig):
    name = sys._getframe().f_code.co_name
