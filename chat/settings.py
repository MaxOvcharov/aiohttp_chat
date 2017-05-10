import os
import logging

from optparse import OptionParser

__all__ = ['logger', 'parse_args_for_run_server',
           'parse_args_for_migrate_db', 'BASE_DIR']

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


logger = logging.getLogger('app')
logger.setLevel(logging.DEBUG)

f = logging.Formatter('[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
                      datefmt='%Y-%m-%d %H:%M:%S')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(f)
logger.addHandler(ch)


def parse_args_for_run_server():
    """
    Configurations of arg-parser for run_server.py
    :return: options - a dict with input args
    """
    parser = OptionParser()
    parser.add_option('--path', dest='path',
                      help='PATH TO UNIX SOCKET',
                      metavar='PATH TO UNIX SOCKET',
                      default=None)
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

    return options


def parse_args_for_migrate_db():
    """
    Configurations of arg-parser for migrate_db.py
    :return: options - a dict with input args
    """
    parser = OptionParser()
    parser.add_option('-a', '--all', dest='all',
                      help='MIGRATE TABLES AND INSERT DATA',
                      action='store_true')
    parser.add_option('-m', '--migrate-only', dest='migrate_only',
                      help='MIGRATE TABLES',
                      action='store_true')
    parser.add_option('-i', '--insert', dest='insert',
                      help='INSERT DATA INTO TABLES',
                      action='store_true')
    (options, args) = parser.parse_args()

    if not options.all and not options.migrate_only and not options.insert:
        parser.error('One args is mandatory for running migrate_db.py. See --help')

    return options
