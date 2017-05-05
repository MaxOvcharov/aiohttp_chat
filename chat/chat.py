import aiofiles
import base64
import gzip
import hashlib
import socketio

# from small_talk import run_small_talk
from settings import logger
from models import save_private_history
from server_message import get_server_message

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
            if message.get('data') is not None:
                # api_ai_message = await run_small_talk(message['data'])  # TODO change to the json server_message
                api_ai_message = await get_server_message(message['data'])
                await sio.emit('sendMessageResponse',
                               {'data': api_ai_message},
                               room=sid, namespace='/chat')
                async with sio.pg.acquire() as conn:
                    await save_private_history(conn, message)
                logger.debug('EVENT: "sendMessage"(ECHO), SID: %s Message: %s' % (sid, message))
            else:
                raise ValueError('Message should have key("data")')
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
