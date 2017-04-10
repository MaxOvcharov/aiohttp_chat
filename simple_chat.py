# -*- coding: utf-8 -*-

import argparse
import logging
import socketio

from aiohttp import web

sio = socketio.AsyncServer(async_mode='aiohttp')
app = web.Application()
sio.attach(app)

logger = logging.getLogger('app')
logger.setLevel(logging.DEBUG)

f = logging.Formatter('[L:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(f)
logger.addHandler(ch)

parser = argparse.ArgumentParser(description="aiohttp server example")
parser.add_argument('--path')
parser.add_argument('--port')

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
    logger.debug('My EVENT(%s): %s' % (sid, message))
    await sio.emit('my response', {'data': message['data']}, room=sid)


@sio.on('my broadcast event', namespace='/test')
async def join(sid, message):
    sio.enter_room(sid, message['room'], namespace='/test')
    await sio.emit('my response', {'data': 'Entered room: ' + message['room']},
                   room=sid, namespace='test')


@sio.on('join', namespace='/test')
async def join(sid, message):
    sio.enter_room(sid, message['room'], namespace='/test')
    await sio.emit('my response', {'data': 'Entered room: ' + message['room']},
                   room=sid, namespace='/test')


@sio.on('leave', namespace='/test')
async def leave(sid, message):
    sio.leave_room(sid, message['room'], namespace='/test')
    await sio.emit('my response', {'data': 'Left room: ' + message['room']},
                   room=sid, namespace='/test')


@sio.on('close room', namespace='/test')
async def close(sid, message):
    await sio.emit('my response', {'data': 'Room %s is closing' % message['room']},
                   room=message['room'], namespace='/test')
    await sio.close_room(message['room'], namespace='/test')


@sio.on('my room event', namespace='/test')
async def send_room_message(sid, message):
    logger.debug('ROOM EVENT(%s): %s' % (sid, message))
    await sio.emit('my response', {'data': message['data']},
                   room=message['room'], namespace='/test')


@sio.on('disconnect request', namespace='/test')
async def disconnect_request(sid):
    await sio.disconnect(sid, namespace='/test')


@sio.on('connect', namespace='/test')
async def test_connect(sid, environ):
    await sio.emit('my response', {'data': 'Connected', 'count': 0},
                   room=sid, namespace='/test')


@sio.on('disconnect', namespace='/test')
def test_disconnect(sid):
    print('Client disconnected')


app.router.add_static('/static', 'static')
app.router.add_get('/', index)


if __name__ == '__main__':
    args = parser.parse_args()
    sio.start_background_task(background_task)
    web.run_app(app, path=args.path, port=args.port)


