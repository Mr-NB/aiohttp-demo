import logging, pathlib, jinja2, aiohttp_jinja2
import aiohttp_autoreload
import aiohttp, asyncio, os
from aiohttp import web
from aiohttp_swagger import *
from app.config import MongoConfig, Local, Dev, BaseConfig, Pro
from app import app
from aiohttp.log import web_logger

TEMPLATES_ROOT = pathlib.Path(__file__).parent / 'app/templates'


def setup_jinja(app):
    loader = jinja2.FileSystemLoader(str(TEMPLATES_ROOT))
    jinja_env = aiohttp_jinja2.setup(app, loader=loader)
    return jinja_env


async def on_startup(app):
    from app.routes import setup_ui_routes
    app.logger = web_logger
    setup_ui_routes(app)
    # 初始化Session
    coon = aiohttp.TCPConnector(limit=10)
    session = aiohttp.ClientSession(connector=coon)
    app.Session = session

    # 初始化Mongo
    # 初始化SchedulerUnpredictableError

    app.logger.info('create session successfully')
    app.logger.info('create mongo-clent successfully')


async def on_cleanup(app):
    await app.Session.close()
    app.logger.info('close Mongo')


async def main(app):
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    setup_jinja(app)
    app.Scheduler.start()

    # aiohttp_session.setup(app, MongoStorage(MongoStorageCollection,max_age=app.config.SessionMaxAge))
    # aiohttp_session.setup(api, MongoStorage(MongoStorageCollection,max_age=app.config.SessionMaxAge))
    return app


if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
        level=logging.INFO)
    aiohttp_autoreload.start()
    # setup_swagger(app,swagger_url='/doc',swagger_from_file="./swagger/swagger.yaml")
    web.run_app(main(app), host=os.getenv("SERVER_HOST", '0.0.0.0'), port=int(os.getenv('SERVER_PORT', 8083)))
