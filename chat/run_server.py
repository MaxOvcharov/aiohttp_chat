# -*- coding: utf-8 -*-
import asyncio
import os

from aiohttp import web

from chat import sio, run_chat
from models import setup_pg
from settings import set_logger, BASE_DIR, parse_args
from utils import load_config
from views import index

# setup logger for app
logger = set_logger()


async def init(loop):
    # global pg
    app = web.Application(loop=loop)

    # load config from yaml file
    conf = load_config(os.path.join(BASE_DIR, "config/dev.yml"))
    pg = await setup_pg(app, conf, loop)

    # Attach app to the Socket.io server
    sio.attach(app)
    # async with pg.acquire() as conn:
    await run_chat(pg)
    # setup views and routes
    app.router.add_static('/static', os.path.join(BASE_DIR, "chat/static/"))
    app.router.add_get('/', index)
    return app


def main():
    options = parse_args()
    # Run background task
    # sio.start_background_task(background_task)
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init(loop))
    # Run app
    web.run_app(app, host=options.host, path=options.path, port=options.port)

if __name__ == '__main__':
    main()
