import aiofiles
import base64
import gzip
import json
import hashlib
import socketio

from settings import logger
from models import users, private_history

# setup application and extensions
sio = socketio.AsyncServer(async_mode='aiohttp',
                           allow_upgrades=True)


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


@sio.on('sendMessage', namespace='/chat')
async def send_message(sid, message):
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
                           room=sid, namespace='/chat')
            async with sio.pg.acquire() as conn:
                async with conn.begin():
                    uid = await conn.scalar(users.insert().values(login='max12', password='121212'))
                    await conn.execute(private_history.
                                       insert().
                                       values(message_id=1,
                                              message_json=json.dumps(
                                                  {'test': message.get('data', 'Wrong data was sent')}),
                                              user_id=uid,
                                              chat_id='test_chat'))
            logger.debug('EVENT: "sendMessage"(ECHO), SID: %s Message: %s' % (sid, message))
        else:
            raise TypeError('Message should be dict: {"data": "some text"}')
    except ValueError as e:
        logger.error('Handle ERROR: %s' % e)
    except TypeError as e1:
        logger.error('Handle ERROR: %s' % e1)


@sio.on('sendFile', namespace='/chat')
async def send_binary_message(sid):
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
                   namespace='/chat',
                   callback=call_back_from_client)
    logger.debug('My EVENT(FILE) (%s): %s' % (sid, content_b64[:20]))
    del content_b64


@sio.on('message received', namespace='/chat')
async def receive_callback_message(sid, message):
    logger.debug('My EVENT(CALL BACK) (%s): %s' % (sid, message))
    return True


@sio.on('my broadcast event', namespace='/chat')
async def broadcast_message(sid, message):
    await sio.emit('my response', {'data': message['data']}, namespace='/chat')
    logger.debug('BROADCAST MESSAGE(%s): %s' % (sid, message))


@sio.on('join', namespace='/chat')
async def join_room(sid, message):
    sio.enter_room(sid, message['room'], namespace='/chat')
    await sio.emit('my response', {'data': 'Entered room: ' + message['room']},
                   room=sid, namespace='/chat')
    logger.debug('JOIN ROOM (%s): %s' % (sid, message))


@sio.on('leave', namespace='/chat')
async def leave_room(sid, message):
    sio.leave_room(sid, message['room'], namespace='/chat')
    await sio.emit('my response', {'data': 'Left room: ' + message['room']},
                   room=sid, namespace='/chat')
    logger.debug('LEAVE ROOM (%s): %s' % (sid, message))


@sio.on('close room', namespace='/chat')
async def close(sid, message):
    await sio.emit('my response', {'data': 'Room %s is closing' % message['room']},
                   room=message['room'], namespace='/chat')
    await sio.close_room(message['room'], namespace='/chat')
    logger.debug('CLOSE ROOM (%s): %s' % (sid, message))


@sio.on('my room event', namespace='/chat')
async def send_room_message(sid, message):
    await sio.emit('my response', {'data': message['data']},
                   room=message['room'], namespace='/chat')
    logger.debug('ROOM EVENT (%s): %s' % (sid, message))


@sio.on('disconnect request', namespace='/chat')
async def disconnect_request(sid):
    await sio.disconnect(sid, namespace='/chat')
    logger.debug('DISCONNECT REQUEST: %s' % sid)


@sio.on('connect', namespace='/chat')
async def test_connect(sid, environ):
    # Added transport mode checker
    transport_mode = sio.transport(sid)
    logger.debug('CONNECT TRANSPORT MODE (%s): %s' % (sid, transport_mode))

    await sio.emit('my response', {'data': 'Connected', 'count': 0},
                   room=sid, namespace='/chat')
    logger.debug('CONNECT USER: %s, ENVIRON: %s' % (sid, environ))


@sio.on('disconnect', namespace='/chat')
def test_disconnect(sid):
    logger.debug('DISCONNECT USER: %s' % sid)
