# @Eamil    : iamfuture_x@outlook.com
# @Author  : Mr-NB

from aiohttp import web
import aiohttp_cors, pathlib

from app.routes.common import app_routes
from app.routes.api import api_routes
from aiohttp_swagger3 import SwaggerUiSettings, SwaggerDocs

static_path = str(pathlib.Path(__file__).parent.parent / "static")


def setup_app_routes(app):
    """
    :param app:
    :return:
    """
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })
    app.router.add_routes(app_routes)
    # s = SwaggerDocs(app, swagger_ui_settings=SwaggerUiSettings(path="/docs"))
    # s.add_routes(app_routes)
    for route in list(app.router.routes()):
        cors.add(route)
    # app.router.add_static('/static/', path=static_path, name='static')


def setup_api_routes(api):
    """
    :param app:
    :return:
    """
    # pass
    api.router.add_routes(api_routes)
    s = SwaggerDocs(api, swagger_ui_settings=SwaggerUiSettings(path="/docs"), title="Agro-Cloud-Doctor",
                    version="1.0.0",
                    components="components.yaml")
    s.add_routes(api_routes)

    # app.router.add_route('*', '/white-list', api_views.WhiteList)
    # app.router.add_route('*', '/block-list', api_views.BlockList)
    # app.router.add_route('*', '/active-list', api_views.Active)
    # app.router.add_route('*', '/email_settings', api_views.EmailSettings)
