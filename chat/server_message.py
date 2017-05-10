# -*- coding: utf-8 -*-
import asyncio
import json
import os
import psycopg2

from aiohttp import web
from datetime import datetime
from random import choice

from models import get_next_message_num, setup_pg
from settings import BASE_DIR, logger
from small_talk import run_small_talk
from utils import load_config

__all__ = ['get_server_message']

async def _prepare_client_message(pg, user_message):
    chat_list = ['CHAT_1', 'CHAT_2', 'CHAT_3', 'CHAT_4']
    async with pg.acquire() as conn:
        try:
            query = table.insert().values(values)
            await conn.execute(query)
        except psycopg2.ProgrammingError as e:
            logger.error('INSERT_DATA_INTO: %s' % e)

    client_message_data = {
        'user_id': ,
        'session_id': 'UNKNOWN USER',
        'chat_id': choice(chat_list),
        'pgta_api': {
            'message': {
            'date': datetime.now(),
            'text': user_message,
            'message_id': 4508,
            'from': {
               'first_name': 'FIRST NAME',
               'last_name': 'LAST NAME',
               'id': '4f5bc00e-8516-49a9-8507-d475d40d06b5'
             },
             'chat': {
               'id': '4f5bc00e-8516-49a9-8507-d475d40d06b5',
               'title': 'CHAT NAME'
             }
           },
           'update_id': 557085855
         }
        }


async def _prepare_server_message(message_num, user_message):
    message_data = {
        'message': {
            'date': datetime.now(),
            'text': await run_small_talk(user_message),
            'message_id': message_num,
            'chat': {
                'id': 1,
                'title': 'TEST CHAT ROOM'
            },
            'update_id': 557085875
        }
    }
    return json.dumps(message_data)


async def get_server_message(pg, message):

    async with pg.acquire() as conn:
        message_num = await get_next_message_num(conn, message['user_id'])
    server_message = await _prepare_server_message(message_num,
                                                   message['pgta_api']['message']['text'])
    return server_message


async def main(loop, message_text):
    app = web.Application(loop=loop)
    # load config from yaml file
    conf = load_config(os.path.join(BASE_DIR, "config/dev.yml"))
    pg = await setup_pg(app, conf, loop)
    message_json = await _prepare_client_message(pg, message_text)
    res = await get_server_message(pg, message_json)
    print('API_AI: %s' % res)

if __name__ == '__main__':
    message_text = input("Введите фразу: ")
    loop = asyncio.get_event_loop()
    task = [asyncio.ensure_future(main(loop, message_text))]
    loop.run_until_complete(asyncio.wait(task))
    loop.close()
