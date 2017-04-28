# import sqlalchemy as sa
import os
import uuid

import aiopg.sa
from sqlalchemy import MetaData
from sqlalchemy import ForeignKey
from sqlalchemy import Table, Column
from sqlalchemy import Integer, String, Text, Boolean
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID, JSON


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
              Column('login', String(255), nullable=False),
              Column('password', Text, nullable=False),
              Column('user_id', GUID(), default=uuid.uuid4, nullable=False, unique=True),
              )

unknown_users = Table('unknown_users', metadata,
                      Column('id', Integer, primary_key=True),
                      Column('session_id', GUID(), default=uuid.uuid4, nullable=False, unique=True),)


users_to_unknown_users = Table('users_to_unknown_users', metadata,
                               Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE')),
                               Column('user_id', Integer, ForeignKey('unknown_users.id', ondelete='CASCADE')))

private_history = Table('private_history', metadata,
                        Column('id', Integer, primary_key=True),
                        Column('message_id', Integer, nullable=True),
                        Column('message_json', JSON, server_default='{}'),
                        Column('user_id', GUID(), ForeignKey('users.user_id')),
                        Column('chat_id', String, nullable=False))

public_history = Table('public_history', metadata,
                       Column('id', Integer, primary_key=True),
                       Column('message_id', Integer, nullable=True),
                       Column('message_json', JSON, server_default='{}'),
                       Column('unknown_user_id', GUID(), ForeignKey('unknown_users.session_id')),
                       Column('chat_id', String, nullable=False))


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
