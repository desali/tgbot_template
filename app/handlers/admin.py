from aiogram import Dispatcher
from aiogram.types import Message

from models.role import UserRole


async def admin_start(message: Message):
    await message.reply("Hello, admin!")


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_start, commands=["start"], state="*", role=[UserRole.ADMIN])
