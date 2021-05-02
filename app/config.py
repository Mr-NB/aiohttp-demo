import os, sys
from enum import Enum


class BaseConfig:
    pass


class Local(BaseConfig):
    name = sys._getframe().f_code.co_name

    @property
    def config(self):
        return {}


class Pro(BaseConfig):
    name = sys._getframe().f_code.co_name

    @property
    async def config(self):
        return {}


class Dev(BaseConfig):
    name = sys._getframe().f_code.co_name

    @property
    async def config(self):
        return {}


class CodeStatus(Enum):
    SuccessCode = 200
    Unauthorized = 401
    NotFound = 404
    BadRequest = 400
    UnknownError = 500
    Timeout = 504
    CmsUndoPublishError = 156
    PermissionDenied = 104
    FormatError = 105
    ParametersMissError = 106
    ParametersTypeError = 107
    InvalidDataError = 108
    DataDuplicateError = 109


class WorkStatusMapping(Enum):
    awaiting = "待上报"
    pending = "待审核"
    success = "审核通过"
    failed = "审核未通过"


class RoleMapping(Enum):
    admin = "ADMIN"
    worker = "FARM_WORKER"
