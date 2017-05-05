import asyncio
import os
import psycopg2

from faker import Factory
from sqlalchemy.schema import CreateTable, DropTable

import models
from settings import logger, BASE_DIR
from utils import load_config


async def delete_tables(pg, tables):
    """
    Delete tables from DB before creating new version
    :param pg: postgres engine
    :param tables: tables from models.py
    :return: None
    """
    async with pg.acquire() as conn:
        for table in reversed(tables):
            drop_expr = DropTable(table)
            try:
                await conn.execute(drop_expr)
                logger.debug('DB_DELETE: %s' % table)
            except psycopg2.ProgrammingError as e:
                logger.error('DB_DELETE: %s' % e)

async def prepare_table(pg):
    """
    Get all tables from models.py and delete them
    :param pg: postgres engine
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

async def init(loop):
    logger.debug('DB_START: start uploading new version of tables')
    # load config from yaml file
    conf = load_config(os.path.join(BASE_DIR, "config/dev.yml"))
    pg = await models.init_postgres(conf['postgres'], loop)
    await prepare_table(pg)
    logger.debug('DB_END: All tables was uploaded successfully')


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop))


if __name__ == '__main__':
    main()