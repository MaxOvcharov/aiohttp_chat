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
    return user_id


@pytest.fixture(params=[(1, False), (2, False), (3, False),
                        (4, True), (5, True), (6, True)])
def params_get_or_create_user_metod_positive(request, get_user_id_for_param):
    if request.param[0] <= 3:
        return get_user_id_for_param, request.param[1]
    else:
        return uuid.uuid4(), request.param[1]


@pytest.mark.run_loop
async def test_get_or_create_user_metod(pg, create_table, params_get_or_create_user_metod_positive):
    input_user_id, input_res_of_creating = params_get_or_create_user_metod_positive
    async with pg.acquire() as conn:
        user_id, res_of_creating = await get_or_create_user(conn, input_user_id)
    assert res_of_creating == input_res_of_creating
