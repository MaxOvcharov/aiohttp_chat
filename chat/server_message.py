# -*- coding: utf-8 -*-
import asyncio
import json

from datetime import datetime

from small_talk import run_small_talk
from models import get_next_message_num

__all__ = ['get_server_message']

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


async def main(message):
    res = await get_server_message(message)
    print('API_AI: %s' % res)

if __name__ == '__main__':
    user_message = input("Введите фразу: ")
    loop = asyncio.get_event_loop()
    task = [asyncio.ensure_future(main(user_message))]
    loop.run_until_complete(asyncio.wait(task))
    loop.close()
