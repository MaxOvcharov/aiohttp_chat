import logging
from optparse import OptionParser

#############################################
#                                           #
#         Configurations of logger          #
#                                           #
#############################################
logger = logging.getLogger('app')
logger.setLevel(logging.DEBUG)

f = logging.Formatter('[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
                      datefmt='%Y-%m-%d %H:%M:%S')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(f)
logger.addHandler(ch)

#############################################
#                                           #
#         Configurations of arg-parser      #
#                                           #
#############################################

parser = OptionParser()
parser.add_option('--path', dest='path',
                  help='PATH TO UNIX SOCKET',
                  metavar='PATH TO UNIX SOCKET')
parser.add_option('--port', dest='port', type='int',
                  help='PORT FOR HTTP CONNECTION',
                  metavar='PORT FOR HTTP CONNECTION')
parser.add_option('--host', dest='host',
                  help='HOST NAME',
                  default='127.0.0.2',
                  metavar='HOST NAME')
(options, args) = parser.parse_args()

if not options.port:
    parser.error('PORT is mandatory for running app')


# try:
#     from aiohttp_chat.local_settings import *
# except ImportError:
#     pass