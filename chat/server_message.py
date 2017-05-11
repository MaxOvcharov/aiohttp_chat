# -*- coding: utf-8 -*-
import asyncio
import json
import os
from uuid import UUID

from aiohttp import web
from datetime import datetime, date
from random import choice

from models import get_next_message_num, get_data_for_client_message, \
                        save_private_history, setup_pg
from settings import BASE_DIR, logger
from small_talk import run_small_talk
from utils import load_config

__all__ = ['get_server_message']


class JSONEncoder_newdefault(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%SZ')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, UUID):
            return str(obj)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

async def _prepare_client_message(pg, user_message):
    chat_list = ['CHAT_1', 'CHAT_2', 'CHAT_3', 'CHAT_4']
    async with pg.acquire() as conn:
        user, message_num, chat_id = await get_data_for_client_message(conn)

    client_message_data = {
        'user_id': user['user_id'],
        'session_id': 'UNKNOWN USER',
        'chat_id': choice(chat_list),
        'pgta_api': {
            'message': {
                'date': datetime.now(),
                'text': user_message,
                'message_id': message_num,
                'from': {
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'id': user['user_id'],
                    },
                'chat': {
                    'id': chat_id,
                    'title': chat_id.split('_')[0]
                    }
            },
        }
    }
    return json.dumps(client_message_data, cls=JSONEncoder_newdefault)

async def _prepare_server_message(message_num, chat_id, message_text):
    message_data = {
        'message': {
            'date': datetime.now(),
            'text': await run_small_talk(message_text),
            'message_id': message_num,
            'chat': {
                'id': chat_id,
                'title': chat_id.split('_')[0]
            },
        }
    }
    return json.dumps(message_data, cls=JSONEncoder_newdefault)

async def get_server_message(pg, client_message):
    client_message = json.loads(client_message)
    client_message_data = {
        'user_id': client_message.get('user_id'),
        'chat_id': client_message.get('pgta_api').get('message').get('chat').get('id'),
        'message_json': json.dumps(client_message.get('pgta_api'),
                                   cls=JSONEncoder_newdefault)
    }

    # Save message from client
    async with pg.acquire() as conn:  # TODO add check if api doesn't response
        message_num = await save_private_history(conn, client_message_data)

    server_message = await _prepare_server_message(message_num,
                                                   client_message.get('pgta_api')
                                                   .get('message')
                                                   .get('chat')
                                                   .get('id'),
                                                   client_message.get('pgta_api')
                                                   .get('message')
                                                   .get('text'))

    server_message_data = {
        'user_id': client_message.get('user_id'),
        'chat_id': client_message.get('pgta_api').get('message').get('chat').get('id'),
        'message_json': server_message
    }
    # Save message from server
    async with pg.acquire() as conn:  # TODO add check if api doesn't response
        await save_private_history(conn, server_message_data)

    return server_message

async def main(loop, input_message_text):
    app = web.Application(loop=loop)
    # load config from yaml file
    conf = load_config(os.path.join(BASE_DIR, "config/dev.yml"))
    pg = await setup_pg(app, conf, loop)
    message_json = await _prepare_client_message(pg, input_message_text)
    server_message = await get_server_message(pg, message_json)
    logger.debug("Message with API.ai response: %s" % server_message)

if __name__ == '__main__':
    input_message_text = input("Введите фразу: ")
    loop = asyncio.get_event_loop()
    task = [asyncio.ensure_future(main(loop, input_message_text))]
    loop.run_until_complete(asyncio.wait(task))
    loop.close()
