import aiopg.sa
import os
import pytest

import models

from settings import BASE_DIR
from migrate_db import prepare_tables, prepare_insert_data, delete_tables
from utils import load_config


@pytest.fixture
def pg(request, loop):
    async def init_postgres(conf, loop):
        engine = await aiopg.sa.create_engine(
            database=conf['database'],
            user=conf['user'],
            password=conf['password'],
            host=conf['host'],
            port=conf['port'],
            minsize=1,
            maxsize=2,
            loop=loop)
        return engine

    conf = load_config(os.path.join(BASE_DIR, "config/dev.yml"))
    engine = loop.run_until_complete(init_postgres(conf['postgres_test'], loop))

    def fin():
        engine.close()
        loop.run_until_complete(engine.wait_closed())
    request.addfinalizer(fin)
    return engine


@pytest.fixture
def chat_tables():
    sa_tables = [getattr(models, table) for table in models.__all__]
    tables = {}
    for table in sa_tables:
        tables['%s' % table] = table
    return tables


@pytest.fixture()
def create_table(request, chat_tables, loop, pg):
    async def run_db_migration(pg):
        await prepare_tables(pg, verbose=False)
        await prepare_insert_data(pg, verbose=False)

    loop.run_until_complete(run_db_migration(pg))

    # tables = [table for table in chat_tables.values()]
    # async def fin():
    #     await delete_tables(pg, tables, verbose=False)
    #
    # loop.run_until_complete(fin())
