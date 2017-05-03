# -*- coding: utf-8 -*-
import os

from aiohttp import web

from settings import set_logger, BASE_DIR

# setup logger for app
logger = set_logger()

async def index(request):
    """
    Simple client in web browser
    :param request: request from page
    :return: response app.html file
    """
    with open(os.path.join(BASE_DIR, "chat/templates/app.html")) as f:
        return web.Response(text=f.read(), content_type='text/html')
