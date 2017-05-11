# -*- coding: utf-8 -*-
import os

from aiohttp import web

from settings import BASE_DIR

async def index(request):
    """
    Simple client in web browser
    :param request: request from page
    :return: response app.html file
    """
    with open(os.path.join(BASE_DIR, "chat/templates/app.html")) as f:
    # with open(os.path.join(BASE_DIR, "chat/chat_widget/index.html")) as f:
        return web.Response(text=f.read(), content_type='text/html')
