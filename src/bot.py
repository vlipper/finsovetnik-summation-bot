import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message as MessageTG

from src.data_models import Article, Chat
from src.data_models import Message as MessageDB

logger = logging.getLogger(__name__)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: MessageTG) -> None:
    chat = await Chat.select().where(Chat.chat_id == message.chat.id).first()

    if chat is None:
        await Chat(chat_id=message.chat.id).save()
        await message.answer("You are now subscribed to updates")
    else:
        await message.answer("You are already subscribed to updates")


async def spread_message(
    bot: Bot,
    article: Article,
) -> list[MessageDB]:
    chats = await Chat.select(Chat.chat_id)
    tasks = [bot.send_message(c["chat_id"], text=article.summary) for c in chats]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    messages = []
    for chat, result in zip(chats, results):
        if isinstance(result, BaseException):
            # TODO: add retry for failed messages
            logger.warning(f"Failed to send {chat['chat_id']}", exc_info=result)
            continue
        message = MessageDB(
            message_id=result.message_id,
            chat_id=chat["chat_id"],
            article_id=article.article_id,
        )
        messages.append(message)

    return messages
