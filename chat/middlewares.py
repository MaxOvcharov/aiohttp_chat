from aiohttp import web
from aiohttp_session import get_session


async def authorize(app, handler):
    async def middleware(request):
        def check_path(path):
            result = True
            for r in ['/login', '/signin', '/signout']:
                if path.startswith(r):
                    result = False
            return result

        session = await get_session(request)
        if session.get("user"):
            return await handler(request)
        elif check_path(request.path):
            url = request.app.router['login'].url()
            raise web.HTTPFound(url)
        else:
            return await handler(request)

    return middleware