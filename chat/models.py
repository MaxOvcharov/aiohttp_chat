# -*- coding: utf-8 -*-
import aiopg.sa
import random
import uuid


from sqlalchemy import MetaData, exc, desc
from sqlalchemy import ForeignKey
from sqlalchemy import Table, Column
from sqlalchemy import Integer, String, Text, Boolean
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID, JSON

from settings import logger


__all__ = ['users', 'unknown_users', 'users_to_unknown_users',
           'private_history', 'public_history']

metadata = MetaData()


class GUID(TypeDecorator):
    """
    Platform-independent GUID type.
    Uses Postgresql's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.
    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value)
            else:
                # hexstring
                return "%.32x" % value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)

users = Table('users', metadata,
              Column('id', Integer, primary_key=True),
              Column('first_name', String(100), nullable=True),
              Column('last_name', String(100), nullable=True),
              Column('login', String(100), nullable=False),
              Column('email', String(100), nullable=True),
              Column('password', String(100), nullable=False),
              Column('user_id', GUID(), default=uuid.uuid4, nullable=False, unique=True),
              )

unknown_users = Table('unknown_users', metadata,
                      Column('id', Integer, primary_key=True),
                      Column('session_id', GUID(), default=uuid.uuid4, nullable=False, unique=True),)


users_to_unknown_users = Table('users_to_unknown_users', metadata,
                               Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE')),
                               Column('unknown_users_id', Integer, ForeignKey('unknown_users.id', ondelete='CASCADE')))

private_history = Table('private_history', metadata,
                        Column('id', Integer, primary_key=True),
                        Column('message_id', Integer, nullable=True),
                        Column('message_json', JSON, server_default='{}'),
                        Column('user_id', Integer, ForeignKey('users.id')),
                        Column('chat_id', String, nullable=False))

public_history = Table('public_history', metadata,
                       Column('id', Integer, primary_key=True),
                       Column('message_id', Integer, nullable=True),
                       Column('message_json', JSON, server_default='{}'),
                       Column('unknown_user_id', Integer, ForeignKey('unknown_users.id')),
                       Column('chat_id', String, nullable=False))


class RecordNotFound(Exception):
    """Requested record in database was not found"""


async def setup_pg(app, conf, loop):
    # create connection to the database
    pg = await init_postgres(conf['postgres'], loop)

    async def close_pg(app):
        pg.close()
        await pg.wait_closed()

    app.on_cleanup.append(close_pg)
    return pg

async def init_postgres(conf, loop):
    engine = await aiopg.sa.create_engine(
        database=conf['database'],
        user=conf['user'],
        password=conf['password'],
        host=conf['host'],
        port=conf['port'],
        minsize=conf['minsize'],
        maxsize=conf['maxsize'],
        loop=loop)
    return engine

async def get_or_create_user(conn, user_id):
    try:
        uid = await conn.scalar(users.select().where(users.c.user_id == user_id))
        if uid:
            return uid, False
        else:
            uid = await conn.scalar(users.insert().values({'user_id': user_id}))
            return uid, True
    except exc.SQLAlchemyError as e:
        logger.erorr('SQL-method: %s' % e)

async def save_private_history(conn, message_data):
    try:
        async with conn.begin():
            user = await get_or_create_user(conn, message_data['user_id'])  # TODO add first and last name for user
            message_num = await get_next_message_num(conn, user[0])
            await conn.execute(private_history.
                               insert().
                               values(message_id=message_num,
                                      message_json=message_data['message_json'],
                                      user_id=user[0],
                                      chat_id=message_data['chat_id']))
        return message_num + 1
    except exc.SQLAlchemyError as e:
        logger.erorr('SQL-method: %s' % e)

async def get_next_message_num(conn, user_id, chat_id=False):
    """
    Get next number of message and if flag chat_id=True return chat_id
    :param conn: connect to DB engine(PostgreSQL)
    :param user_id: user_id from 'users' table
    :param chat_id: If True: return chat_id for test client_message
    :return: message_num, [chat_id]
    """
    try:
        res = await conn.execute(
            private_history.select().
            where(private_history.c.user_id == user_id).order_by(desc('id'))
        )
        message_num = await res.first()

        if message_num and not chat_id:
            return message_num['message_id'] + 1
        elif message_num and chat_id:
            return message_num['message_id'] + 1, message_num['chat_id']
        else:
            return 1
    except exc.SQLAlchemyError as e:
        logger.erorr('SQL-method: %s' % e)

async def get_data_for_client_message(conn):
    try:
        res = await conn.execute(
            users.select().where(users.c.id == random.randint(1, 10))
        )
        user = await res.fetchone()
        message_num, chat_id = await get_next_message_num(conn, user['id'], chat_id=True)
        return user, message_num, chat_id
    except exc.SQLAlchemyError as e:
        logger.error('SQL-method: %s' % e)

