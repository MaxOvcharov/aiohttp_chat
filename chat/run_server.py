# -*- coding: utf-8 -*-
import asyncio
import jinja2
import os

from aiohttp import web
import aiohttp_jinja2
import aiohttp_debugtoolbar
from aiohttp_session import session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from chat import sio
from models import setup_pg
from routes import routes
from settings import BASE_DIR, DEBUG, parse_args_for_run_server
from utils import load_config

from middlewares import authorize


async def init(loop):
    # load config from yaml file
    conf = load_config(os.path.join(BASE_DIR, "config/dev.yml"))

    middle = [
        session_middleware(EncryptedCookieStorage(conf['cookes']['secret_key'])),
        authorize,
    ]
    if DEBUG:
        middle.append(aiohttp_debugtoolbar.middleware)

    app = web.Application(loop=loop, middlewares=middle)

    sio.pg = await setup_pg(app, conf, loop)

    # Attach app to the Socket.io server
    sio.attach(app)
    # setup views and routes
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))
    app.router.add_static('/static', os.path.join(BASE_DIR, "chat/static"), name='static')
    # app.router.add_static('/css', os.path.join(BASE_DIR, "chat/chat_widget/css"))
    # app.router.add_static('/js', os.path.join(BASE_DIR, "chat/chat_widget/js"))
    # app.router.add_static('/fonts', os.path.join(BASE_DIR, "chat/chat_widget/fonts"))
    # route part
    for route in routes:
        app.router.add_route(route[0], route[1], route[2], name=route[3])
    return app


def main():
    options = parse_args_for_run_server()
    # Run background task
    # sio.start_background_task(background_task)
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init(loop))
    # Run app
    web.run_app(app, host=options.host, path=options.path, port=options.port)

if __name__ == '__main__':
    main()
