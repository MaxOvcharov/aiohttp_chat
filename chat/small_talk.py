# -*- coding: utf-8 -*-
import asyncio
import json
import multiprocessing
import os.path
import sys
try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai

from concurrent.futures import ThreadPoolExecutor

from settings import logger, BASE_DIR
from utils import load_config

__all__ = ['run_small_talk']

# load config from yaml file
conf = load_config(os.path.join(BASE_DIR, "config/dev.yml"))
api_ai_conf = conf['api_ai']


def _small_talk(message="Привет"):
    """
        This method connect to Api.ai Small Talk domain
        :param message: input message
        :return: output message from Api.ai
    """
    ai = apiai.ApiAI(api_ai_conf['client_access_token'])
    request = ai.text_request()
    request.lang = 'ru'  # optional, default value equal 'en'
    request.session_id = api_ai_conf['sessid'][:35]
    request.query = message

    response = request.getresponse().read()
    obj = json.loads(response.decode('utf-8'))
    try:
        alternate_result = obj.get('alternateResult')
        if not alternate_result:
            # If response with answer from domain(result) - Small Talk
            answer = obj.get('result').get('fulfillment').get('speech')
            return answer
        else:
            answer_from_domain = obj.get('alternateResult').get('fulfillment').get('speech')
            if not answer_from_domain:
                # If response with answer from agent(result)
                answer = obj.get('result').get('fulfillment').get('speech')
                return answer
            else:
                # If response with answer from domain(alternate result) - Small Talk
                return answer_from_domain
    except AttributeError as e:
        logger.error('Handle ERROR: {0}'.format(e))


@asyncio.coroutine
def run_small_talk(message):
    pool = ThreadPoolExecutor(max_workers=multiprocessing.cpu_count())
    st_loop = asyncio.get_event_loop()
    future_api_ai_message = st_loop.run_in_executor(pool, _small_talk, message)
    return future_api_ai_message


async def main(message):
    res = await run_small_talk(message)
    print('API_AI: %s' % res)


if __name__ == '__main__':
    user_message = input("Введите фразу: ")
    loop = asyncio.get_event_loop()
    task = [asyncio.ensure_future(main(user_message))]
    loop.run_until_complete(asyncio.wait(task))
    loop.close()

