# @Eamil    : iamfuture_x@outlook.com
# @Author  : Mr-NB
from uuid import uuid4
from time import time

from tortoise import fields
from app.models import BaseModel
from app.config import WorkStatusMapping
from app.util import Util


class WorkModel(BaseModel):
    '''
    农事表
    '''

    class Meta:
        table = "agro_cloud_doctor_work"

    plant_id = fields.IntField(null=True)
    operator_id = fields.IntField(null=True)
    operator_name = fields.CharField(40, null=True)
    content = fields.TextField(default="")
    work_type = fields.CharField(50, default="")
    assigner = fields.CharField(40, default="")
    assigner_id = fields.IntField(null=True)
    approver = fields.CharField(40, default="")
    approver_id = fields.IntField(null=True)
    aim_datetime = fields.DatetimeField(null=True)
    start_datetime = fields.DatetimeField(null=True)
    end_datetime = fields.DatetimeField(null=True)
    # cost = fields.DecimalField(max_digits=15, decimal_places=3)
    status = fields.CharEnumField(WorkStatusMapping, default=WorkStatusMapping.awaiting)
    snapshot = fields.TextField(default="")
    commitStatus = fields.SmallIntField(default=0)
    isShow = fields.SmallIntField(default=0)  # 是否展示
    work_hours = fields.FloatField(default=0.0)
    customer_id = fields.IntField()
    # 种植位置
    plant_position = fields.CharField(255, default="")

    def __str__(self):
        return self.id

    @classmethod
    async def get_statistic(cls, userId):
        works = await cls.filter(operator_id=userId, status=WorkStatusMapping.success.value).all()
        totalSeconds = 0
        for item in works:
            totalSeconds += (item.start_datetime - item.end_datetime).total_seconds()
        return totalSeconds
