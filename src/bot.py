import asyncio

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy import select

from src.constants import BOT_TOKEN
from src.data_models import AsyncSessionMaker, Chat

rt = Router(name=__name__)


def get_bot_n_dispatcher() -> tuple[Bot, Dispatcher]:
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(rt)

    return bot, dp


@rt.message(CommandStart())
async def start_handler(
    message: Message,
    db_session_maker: AsyncSessionMaker,
) -> None:
    chat_id = message.chat.id

    async with db_session_maker.begin() as db_session:
        # check if the chat already exists
        chat_exists = await db_session.get(Chat, chat_id) is not None
        if chat_exists:
            await message.answer("You are already subscribed to updates!")
            return

        db_session.add(Chat(chat_id=chat_id))

    await message.answer("You are now subscribed to updates!")


async def spread_message(
    bot: Bot,
    message: str,
    db_session_maker: AsyncSessionMaker,
) -> None:
    async with db_session_maker() as db_session:
        result = await db_session.execute(select(Chat))
        for chat in result.scalars():
            asyncio.create_task(
                bot.send_message(chat_id=chat.chat_id, text=message, disable_notification=True)
                # parse_mode="MarkdownV2",
            )
