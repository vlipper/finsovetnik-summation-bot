import asyncio

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from src.constants import BOT_TOKEN
from src.data_models import Chat

rt = Router(name=__name__)


def get_bot_n_dispatcher() -> tuple[Bot, Dispatcher]:
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(rt)

    return bot, dp


@rt.message(CommandStart())
async def start_handler(message: Message) -> None:
    chat = await Chat.select().where(Chat.chat_id == message.chat.id).first()

    if chat is None:
        await Chat(chat_id=message.chat.id).save()
        await message.answer("You are now subscribed to updates")
    else:
        await message.answer("You are already subscribed to updates")


async def spread_message(
    bot: Bot,
    message: str,
) -> None:
    chats = await Chat.select(Chat.chat_id)
    for chat in chats:
        asyncio.create_task(bot.send_message(chat_id=chat["chat_id"], text=message))
        # parse_mode="MarkdownV2",
