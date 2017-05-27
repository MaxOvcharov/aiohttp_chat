import pytest
import random
import uuid
from models import get_or_create_user


@pytest.fixture
def get_user_id_for_param(pg, chat_tables, loop):
    async def get_user_id(pg, chat_tables):
        async with pg.acquire() as conn:
            res = await conn.execute(
                chat_tables['users'].select().where(chat_tables['users'].c.id == random.randint(1, 10))
            )
            user = await res.fetchone()
            return user['user_id']
    user_id = loop.run_until_complete(get_user_id(pg, chat_tables))
    # user_id = await get_user_id(pg, chat_tables)
    return user_id


@pytest.fixture(params=[(1, True), (2, True), (3, True),
                        (4, False), (5, False), (6, False)])
def params_get_or_create_user_metod_positive(request, get_user_id_for_param):
    if request.param[0] in range(1, 4):
        return get_user_id_for_param
    else:
        return uuid.uuid4()


@pytest.mark.usefixtures('params_get_or_create_user_metod_positive')
async def test_get_or_create_user_metod(create_table):
    t = params_get_or_create_user_metod_positive
    print(t)
