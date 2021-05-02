# @Eamil    : iamfuture_x@outlook.com
# @Author  : Mr-NB
import logging, pathlib

import aiohttp_autoreload, aioredis, jinja2, aiohttp_jinja2
import aiohttp
from aiohttp import web
from tortoise.contrib.aiohttp import register_tortoise

from app.config import *
from aiohttp.log import web_logger

TEMPLATES_ROOT = pathlib.Path(__file__).parent / 'app/templates'


def setup_jinja(app):
    loader = jinja2.FileSystemLoader(str(TEMPLATES_ROOT))
    jinja_env = aiohttp_jinja2.setup(app, loader=loader)
    return jinja_env


async def on_startup(app):
    app.logger = web_logger
    # init request session
    coon = aiohttp.TCPConnector(verify_ssl=False)
    session = aiohttp.ClientSession(connector=coon, trust_env=True)
    app.Session = session
    app.redis = await aioredis.create_redis_pool(os.getenv("REDIS", 'redis://localhost'))


async def on_cleanup(app):
    await app.Session.close()
    app.redis.close()
    await app.redis.wait_closed()


async def main():
    from app import app, api
    from app.routes import setup_app_routes, setup_api_routes

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    setup_app_routes(app)
    setup_api_routes(api)
    app.add_subapp('/api/', api)
    setup_jinja(app)
    register_tortoise(
        app, generate_schemas=True, config={
            'connections': {
                'default': os.getenv("MYSQL", 'mysql://root:@localhost:3306/agro_cloud_doctor')
            },
            'apps': {
                'my_app': {
                    'models': ['app.models.model'],
                    'default_connection': 'default',
                }
            },
            'use_tz': False,
            'timezone': "Asia/Shanghai"
        }

    )

    # app.Scheduler.start()
    # aiohttp_session.setup(app, MongoStorage(MongoStorageCollection,max_age=app.config.SessionMaxAge))
    # aiohttp_session.setup(api, MongoStorage(MongoStorageCollection,max_age=app.config.SessionMaxAge))
    return app


if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
        level=logging.INFO)

    aiohttp_autoreload.start()
    web.run_app(main(), host=os.getenv("SERVER_HOST", '0.0.0.0'), port=int(os.getenv('SERVER_PORT', 8083)))
