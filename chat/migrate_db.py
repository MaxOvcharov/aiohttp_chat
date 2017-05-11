import asyncio
import os
import psycopg2
import uuid

from elizabeth import Personal, Text
from random import choice
from sqlalchemy.schema import CreateTable, DropTable

import models
from settings import logger, BASE_DIR, parse_args_for_migrate_db
from utils import load_config


async def delete_tables(pg, tables):
    """
    Delete tables from DB before creating new version
    :param pg: connect to DB engine(PostgreSQL)
    :param tables: tables from models.py
    :return: None
    """
    async with pg.acquire() as conn:
        for table in reversed(tables):
            drop_expr = DropTable(table)
            try:
                await conn.execute(drop_expr)
                # await conn.execute('TRUNCATE %s CASCADE;' % table)
                logger.debug('DB_DELETE: %s' % table)
            except psycopg2.ProgrammingError as e:
                logger.error('DB_DELETE: %s' % e)

async def insert_data(pg, table, values, res=False):
    """
    Universal method for inserting data into table
    :param pg: connect to DB engine(PostgreSQL)
    :param table: table name
    :param values: list of users
    :param res: If true - return result id list
    :return: None or list of table_id
    """
    logger.debug('INSERT_DATA_INTO: %s' % table)
    # logger.debug('INSERT_DATA_INTO: %s' % values)
    # print(values)
    async with pg.acquire() as conn:
        try:
            if res:
                query = table.insert().values(values).\
                    returning(table.c.id)
                cursor = await conn.execute(query)
                resp = await cursor.fetchall()
                return [r[0] for r in resp]
            else:
                query = table.insert().values(values)
                await conn.execute(query)
        except psycopg2.ProgrammingError as e:
            logger.error('INSERT_DATA_INTO: %s' % e)

async def generate_users(pg, rows=20, locale='en'):
    """
    Insert data into users table
    :param pg: connect to DB engine(PostgreSQL)
    :param rows: numbers of rows
    :param locale: language locale
    :return: list of user_id
    """

    values = []
    user = Personal(locale)
    for i in range(rows):
        gender = choice(['female', 'male'])
        values.append({
            'first_name': user.name(gender=gender),
            'last_name': user.surname(gender=gender),
            'user_id': uuid.uuid4(),
        })

    ids = await insert_data(pg, models.users, values, res=True)
    return ids

async def generate_private_history(pg, user_ids, rows=20, locale='ru'):
    """
    Insert data into 'private_history' table. For every 'user_id' insert
    message_num = (rows / len(user_ids)) per user.
    :param pg: connect to DB engine(PostgreSQL)
    :param user_ids: list of 'user_id' from table 'users'
    :param rows: numbers of rows
    :param locale: language locale
    :return: None
    """
    values = []
    user_message = Text(locale=locale)
    messages_per_user = rows // len(user_ids)
    chat_list = ['CHAT_1', 'CHAT_2', 'CHAT_3', 'CHAT_4']
    for user_id in user_ids:
        for message_num in range(1, messages_per_user):
            values.append({
                'message_id': message_num,
                'message_json': {
                    'message': {
                        'text': user_message.sentence(),
                    }
                },
                'user_id': user_id,
                'chat_id': choice(chat_list),
            })
    await insert_data(pg, models.private_history, values)

async def generate_unknown_users(pg, rows=20):
    """
    Insert data into 'unknown_users' table
    :param pg: connect to DB engine(PostgreSQL)
    :param rows: numbers of rows
    :return: list of unknown_user_ids
    """
    values = []
    for i in range(rows):
        values.append({
            'session_id': uuid.uuid4(),
        })

    ids = await insert_data(pg, models.unknown_users, values, res=True)
    return ids

async def generate_public_history(pg, unknown_user_ids, rows=20, locale='ru'):
    """
    Insert data into 'public_history' table. For every 'unknown_user_id' insert
    message_num = (rows / len(unknown_user_ids)) per unknown_user.
    :param pg: connect to DB engine(PostgreSQL)
    :param unknown_user_ids: list of 'unknown_user_id' from table 'unknown_users'
    :param rows: numbers of rows
    :param locale: language locale
    :return: None
    """
    values = []
    user_message = Text(locale=locale)
    messages_per_user = rows // len(unknown_user_ids)
    chat_list = ['CHAT_1', 'CHAT_2']
    for unknown_user_id in unknown_user_ids:
        for message_num in range(1, messages_per_user):
            values.append({
                'message_id': message_num,
                'message_json': {
                    'message': {
                        'text': user_message.sentence(),
                    }
                },
                'unknown_user_id': unknown_user_id,
                'chat_id': choice(chat_list),
            })
    await insert_data(pg, models.public_history, values)

async def generate_users_to_unknown_users(pg, user_ids, unknown_user_ids):
    """
    Insert data into 'users_to_unknown_users' table. For every unknown_user_id insert
    :param pg: connect to DB engine(PostgreSQL)
    :param user_ids:  list of user_id from table 'users'
    :param unknown_user_ids: list of unknown_user_id from table 'unknown_users'
    :return: None
    """
    values = []
    for unknown_user in unknown_user_ids:
        uid = choice(user_ids)
        values.append({
            'user_id': uid,
            'unknown_users_id': unknown_user,
        })
        user_ids.remove(uid)
    await insert_data(pg, models.users_to_unknown_users, values)

async def prepare_tables(pg):
    """
    Get all tables from models.py, delete them and create new tables
    :param pg: connect to DB engine(PostgreSQL)
    :return: None
    """
    tables = [getattr(models, table) for table in models.__all__]
    await delete_tables(pg, tables)
    async with pg.acquire() as conn:
        for table in tables:
            create_expr = CreateTable(table)
            try:
                await conn.execute(create_expr)
                logger.debug('DB_CREATE: %s' % table)
            except psycopg2.ProgrammingError as e:
                logger.error('DB_CREATE(ERROR): %s' % e)

async def prepare_insert_data(pg):
    """
    Insert data into DB tables: users, unknown_users,
    users_to_unknown_users, private_history, public_history
    :param pg: connect to DB engine(PostgreSQL)
    :return: None
    """
    user_ids = await generate_users(pg, rows=50)
    await generate_private_history(pg, user_ids, rows=200)
    unknown_user_ids = await generate_unknown_users(pg, rows=10)
    await generate_public_history(pg, unknown_user_ids, rows=200)
    await generate_users_to_unknown_users(pg, user_ids, unknown_user_ids)

async def init(loop, do_all=None, migrate_only=None, insert=None):
    """
    Initialize DB migration script
    :param loop: global event loop
    :param do_all: If True - migrate tables and insert data
    :param migrate_only: If True - migrate tables only
    :param insert: If True - insert data into tables
    :return: None
    """
    logger.debug('DB_START: start uploading new version of tables')
    # load config from yaml file
    conf = load_config(os.path.join(BASE_DIR, "config/dev.yml"))
    pg = await models.init_postgres(conf['postgres'], loop)
    if do_all:
        await prepare_tables(pg)  # TODO add insert data functions
        await prepare_insert_data(pg)
    elif migrate_only:
        await prepare_tables(pg)
    elif insert:
        await prepare_insert_data(pg)
    logger.debug('DB_END: All tables was uploaded successfully')


def main(opt):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop, do_all=opt.all,
                                 migrate_only=opt.migrate_only,
                                 insert=opt.insert))

if __name__ == '__main__':
    options = parse_args_for_migrate_db()
    main(options)
