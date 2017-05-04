# -*- coding: utf-8 -*-
import asyncio
import functools
import json
import os.path
import signal
import sys

try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai

from settings import logger, BASE_DIR
from utils import load_config

from asyncio.streams import StreamWriter, FlowControlMixin

reader, writer = None, None

# load config from yaml file
conf = load_config(os.path.join(BASE_DIR, "config/dev.yml"))
api_ai_conf = conf['api_ai']


def small_talk(message):
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
    obj = json.loads(response, encoding='utf8')
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


async def stdio(loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()

    stdio_reader = asyncio.StreamReader()
    reader_protocol = asyncio.StreamReaderProtocol(stdio_reader)

    writer_transport, writer_protocol = await loop.connect_write_pipe(FlowControlMixin, os.fdopen(0, 'wb'))
    stdio_writer = StreamWriter(writer_transport, writer_protocol, None, loop)

    await loop.connect_read_pipe(lambda: reader_protocol, sys.stdin)

    return stdio_reader, stdio_writer


async def async_input(message):
    if isinstance(message, str):
        message = message.encode('utf8')

    global reader, writer
    if (reader, writer) == (None, None):
        reader, writer = await stdio()

    writer.write(message)
    await writer.drain()

    line = await reader.readline()
    return line.decode('utf8').replace('\r', '').replace('\n', '')


async def main():
    message = await async_input("Введите фразу: ")
    print('Echo: %s' % message)
    # print(small_talk(message))


def handle_sigterm(loop):
    loop.remove_signal_handler(signal.SIGTERM)
    loop.stop()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGTERM, handle_sigterm, loop)
    try:
        loop.call_soon(functools.partial(main))
        loop.run_forever()
    finally:
        loop.close()
