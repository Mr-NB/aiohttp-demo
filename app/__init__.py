import os, asyncio
from aiohttp import web
from contextvars import ContextVar
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from app.config import Local, MongoConfig
from app.middleware import error_middleware, api_middleware

executors = {
    'default': AsyncIOExecutor(),
}

jobstores = {
    'default': MongoDBJobStore(database=MongoConfig.MongoDB, collection='Schedules', host=MongoConfig.MongoHost)
}

job_defaults = {
    'coalesce': True,
    'max_instances': 5,
    'misfire_grace_time': 600

}
# scheduler = AsyncIOScheduler(executors=executors,jobstores = jobstores,job_defaults = job_defaults)
scheduler = AsyncIOScheduler(executors=executors)
VAR = ContextVar('VAR', default='default')

app = web.Application(middlewares=[error_middleware, api_middleware])
app.Scheduler = scheduler
