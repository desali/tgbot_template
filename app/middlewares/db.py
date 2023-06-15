from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware

from services.repository import Repo


class DbMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    def __init__(self, pool):
        super().__init__()
        self.pool = pool

    async def pre_process(self, obj, data, *args):
        conn = await self.pool.acquire()
        data["conn"] = conn
        data["repo"] = Repo(conn)

    async def post_process(self, obj, data, *args):
        del data["repo"]
        conn = data.get("conn")
        if conn:
            # check the documentation of your pool implementation
            # for proper way of releasing connection
            await self.pool.release(conn)
