import asyncio
import logging

import asyncpg as asyncpg
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from middlewares.db import DbMiddleware
from config import load_config
from filters.role import AdminFilter, RoleFilter
from handlers.admin import register_admin
from handlers.echo import register_echo
from handlers.user import register_user
from middlewares.environment import EnvironmentMiddleware
from middlewares.role import RoleMiddleware

logger = logging.getLogger(__name__)


async def create_pool(host, port, database, user, password):
    max_attempts = 10
    attempt = 0
    while attempt < max_attempts:
        try:
            connection_pool = await asyncpg.create_pool(
                min_size=10,
                max_size=100,
                host=host,
                port=port,
                database=database,
                user=user,
                password=password
            )
            return connection_pool
        except Exception as e:
            print("Database connection failed. Retrying in 5 seconds...")
            await asyncio.sleep(5)
            attempt += 1

    raise Exception("Failed to establish database connection.")


def register_all_middlewares(dp, config, pool):
    dp.setup_middleware(EnvironmentMiddleware(config=config))
    dp.setup_middleware(DbMiddleware(pool))
    dp.setup_middleware(RoleMiddleware(config.tg_bot.admin_ids))


def register_all_filters(dp):
    dp.filters_factory.bind(RoleFilter)
    dp.filters_factory.bind(AdminFilter)


def register_all_handlers(dp):
    register_admin(dp)
    register_user(dp)

    register_echo(dp)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    config = load_config("../.env")
    connection_pool = await create_pool(
        host=config.db.host,
        port=config.db.port,
        database=config.db.database,
        user=config.db.user,
        password=config.db.password,
    )

    if config.tg_bot.use_redis:
        storage = RedisStorage2(
            host=config.redis.host,
            port=config.redis.port,
            db=config.redis.db,
        )
    else:
        storage = MemoryStorage()

    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)

    bot['config'] = config

    register_all_middlewares(dp, config, connection_pool)
    register_all_filters(dp)
    register_all_handlers(dp)

    try:
        await dp.start_polling()
    finally:
        await connection_pool.close()
        await dp.storage.close()
        await dp.storage.wait_closed()
        session = await bot.get_session()
        await session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")
