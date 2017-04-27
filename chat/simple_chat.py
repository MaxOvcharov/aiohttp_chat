# -*- coding: utf-8 -*-

import base64
import gzip
import hashlib

import aiofiles
import socketio
from aiohttp import web

from settings import logger, options
#from ..settings import logger, options


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
    """
    Simple client in web browser
    :param request: request from page
    :return: response app.html file
    """
    with open('templates/app.html') as f:
        return web.Response(text=f.read(), content_type='text/html')


@sio.on('my event', namespace='/test')
async def test_message(sid, message):
    """
    Custom event handler with event_name and
    Socket.IO namespace for the event. This handler works like echo-server.
    :param sid: Session ID of the client
    :param message: message payload
    :return: None
    """
    # Added transport mode checker
    transport_mode = sio.transport(sid)
    logger.debug('MESSAGE TRANSPORT MODE (%s): %s' % (sid, transport_mode))
    try:
        if isinstance(message, dict):
            await sio.emit('my response',
                           {'data': message.get('data', 'Message should be dict: {"data": "some text"}')},
                           room=sid, namespace='/test')
            logger.debug('event: "my event"(ECHO), SID: %s Message: %s' % (sid, message))
        else:
            raise TypeError('Message should be dict: {"data": "some text"}')
    except ValueError as e:
        logger.error('Handle ERROR: %s' % e)
    except TypeError as e1:
        logger.error('Handle ERROR: %s' % e1)


def call_back_from_client(*args, **kwargs):
    """
    Handle callback from client with any parameters
    :param args: positional arguments
    :param kwargs: named arguments
    :return: none
    """

    for arg in args:
        logger.debug('My EVENT(FILE CALLBACK - args) %s' % arg)

    for key, value in kwargs:
        logger.debug('My EVENT(FILE CALLBACK - kwargs) %s:%s' % (key, value))


@sio.on('file', namespace='/test')
async def test_binary_message(sid):
    """
    Custom event handler with event_name and
    Socket.IO namespace for the event. This handler send
    image file in base64 gzip.
    :param sid: Session ID of the client
    :return: emit file base64 gzip
    """
    content_b64 = ''
    hash_sum = ''
    try:
        async with aiofiles.open('static/test.png', mode='rb') as image_file:
            content = await image_file.read()
            gzip_file = gzip.compress(content)
            content_b64 = base64.b64encode(gzip_file)
            hash_sum = hashlib.md5(content_b64).hexdigest()
    except OSError as e:
        logger.error('Handle ERROR: %s' % e)
    await sio.emit('file response',
                   {'data': content_b64.decode('utf-8'), 'hash_sum': hash_sum},
                   room=sid,
                   namespace='/test',
                   callback=call_back_from_client)
    logger.debug('My EVENT(FILE) (%s): %s' % (sid, content_b64[:20]))
    del content_b64


@sio.on('message received', namespace='/test')
async def test_message(sid, message):
    logger.debug('My EVENT(CALL BACK) (%s): %s' % (sid, message))
    return True


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


