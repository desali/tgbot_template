import asyncio
import logging

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


def create_pool(user, password, database, host, echo):
    raise NotImplementedError  # TODO check your db connector


def register_all_middlewares(dp, config, pool):
    dp.setup_middleware(EnvironmentMiddleware(config=config))
    dp.setup_middleware(DbMiddleware(pool))
    dp.setup_middleware(RoleMiddleware(pool))


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
    config = load_config(".env")

    pool = await create_pool(
        user=config.db.user,
        password=config.db.password,
        database=config.db.database,
        host=config.db.host,
        echo=False,
    )

    storage = RedisStorage2() if config.tg_bot.use_redis else MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)

    bot['config'] = config

    register_all_middlewares(dp, config, pool)
    register_all_filters(dp)
    register_all_handlers(dp)

    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
