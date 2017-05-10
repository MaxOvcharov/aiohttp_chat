# -*- coding: utf-8 -*-
import asyncio
import os

from aiohttp import web

from chat import sio
from models import setup_pg
from settings import BASE_DIR, parse_args_for_run_server
from utils import load_config
from views import index


async def init(loop):
    app = web.Application(loop=loop)

    # load config from yaml file
    conf = load_config(os.path.join(BASE_DIR, "config/dev.yml"))
    sio.pg = await setup_pg(app, conf, loop)

    # Attach app to the Socket.io server
    sio.attach(app)
    # setup views and routes
    app.router.add_static('/static', os.path.join(BASE_DIR, "chat/static/"))
    app.router.add_get('/', index)
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
