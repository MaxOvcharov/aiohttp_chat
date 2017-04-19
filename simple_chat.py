# -*- coding: utf-8 -*-

import socketio
import aiofiles
import hashlib

from aiohttp import web
from settings import logger, options

sio = socketio.AsyncServer(async_mode='aiohttp',
                           allow_upgrades=True)
app = web.Application()
sio.attach(app)


async def background_task():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        await sio.sleep(10)
        count += 0
        await sio.emit('my response', {'data': 'Server generated event'},
                       namespace='/test')

async def index(request):
    with open('app.html') as f:
        return web.Response(text=f.read(), content_type='text/html')


@sio.on('my event', namespace='/test')
async def test_message(sid, message):
    # Added transport mode checker
    transport_mode = sio.transport(sid)
    logger.debug('MESSAGE TRANSPORT MODE (%s): %s' % (sid, transport_mode))

    await sio.emit('my response', {'data': message['data']}, room=sid)
    logger.debug('My EVENT (%s): %s' % (sid, message))


@sio.on('file', namespace='/test')
async def test_binary_message(sid, message):
    async with aiofiles.open('test.png', mode='b') as f:
        contents = await f.read()
    hash_sum = hashlib.md5(contents).hexdigest()
    await sio.emit('my response', {'data': contents, 'hash_sum': hash_sum}, room=sid)
    logger.debug('My EVENT(FILE) (%s): %s' % (sid, contents))
    del contents


@sio.on('my broadcast event', namespace='/test')
async def broadcast_message(sid, message):
    await sio.emit('my response', {'data': message['data']}, namespace='/test')
    logger.debug('BROADCAST MESSAGE(%s): %s' % (sid, message))


@sio.on('join', namespace='/test')
async def join(sid, message):
    sio.enter_room(sid, message['room'], namespace='/test')
    await sio.emit('my response', {'data': 'Entered room: ' + message['room']},
                   room=sid, namespace='/test')
    logger.debug('JOIN ROOM (%s): %s' % (sid, message))


@sio.on('leave', namespace='/test')
async def leave(sid, message):
    sio.leave_room(sid, message['room'], namespace='/test')
    await sio.emit('my response', {'data': 'Left room: ' + message['room']},
                   room=sid, namespace='/test')
    logger.debug('LEAVE ROOM (%s): %s' % (sid, message))


@sio.on('close room', namespace='/test')
async def close(sid, message):
    await sio.emit('my response', {'data': 'Room %s is closing' % message['room']},
                   room=message['room'], namespace='/test')
    await sio.close_room(message['room'], namespace='/test')
    logger.debug('CLOSE ROOM (%s): %s' % (sid, message))


@sio.on('my room event', namespace='/test')
async def send_room_message(sid, message):
    # Added transport mode checker
    # transport_mode = sio.transport(sid)
    # logger.debug('TRANSPORT MODE(%s): %s' % (sid, transport_mode))

    await sio.emit('my response', {'data': message['data']},
                   room=message['room'], namespace='/test')
    logger.debug('ROOM EVENT (%s): %s' % (sid, message))


@sio.on('disconnect request', namespace='/test')
async def disconnect_request(sid):
    await sio.disconnect(sid, namespace='/test')
    logger.debug('DISCONNECT REQUEST: %s' % sid)


@sio.on('connect', namespace='/test')
async def test_connect(sid, environ):
    # Added transport mode checker
    transport_mode = sio.transport(sid)
    logger.debug('CONNECT TRANSPORT MODE (%s): %s' % (sid, transport_mode))

    await sio.emit('my response', {'data': 'Connected', 'count': 0},
                   room=sid, namespace='/test')
    logger.debug('CONNECT USER: %s, ENVIRON: %s' % (sid, environ))


@sio.on('disconnect', namespace='/test')
def test_disconnect(sid):
    logger.debug('DISCONNECT USER: %s' % sid)

app.router.add_static('/static', 'static')
app.router.add_get('/', index)

if __name__ == '__main__':

    # Run background task
    # sio.start_background_task(background_task)

    # Run app
    web.run_app(app, host=options.host, path=options.path, port=options.port)


