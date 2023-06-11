from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from services.repository import Repo
from states.user import UserMain


async def user_start(message: Message, repo: Repo, state: FSMContext):
    await repo.add_user(message.from_user.id)
    await message.reply("Hello, user!")
    await state.set_state(UserMain.SOME_STATE)


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state="*")
