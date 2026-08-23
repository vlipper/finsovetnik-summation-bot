import asyncio
import logging

import aiohttp
import litellm
from aiogram import Bot

from src.bot import dp, spread_message
from src.data_models import Message
from src.llm import query_summary
from src.logging_config import setup_logging
from src.scraper import extract_article_content, gen_article_headers, log_in
from src.settings import ARTICLE_MINING_INTERVAL, BOT_POOLING_INTERVAL, BOT_TOKEN

litellm.suppress_debug_info = True  # type: ignore[ty:invalid-assignment]
setup_logging()
logger = logging.getLogger(__name__)


async def periodic_pool() -> None:
    while True:
        try:
            async with Bot(BOT_TOKEN) as bot:
                await dp.start_polling(bot)
        except Exception:
            logger.exception("Error in periodic_pool")
        await asyncio.sleep(BOT_POOLING_INTERVAL)


async def periodic_scrap() -> None:
    while True:
        try:
            async with Bot(BOT_TOKEN) as bot, aiohttp.ClientSession() as http_session:
                http_session = await log_in(http_session)

                # TODO: make synchronized for loop to define new articles and then use async to process them
                async for article_header in gen_article_headers(http_session):
                    html = await article_header.fetch_html(http_session)
                    content = extract_article_content(html)
                    summary = await query_summary(content)
                    article = article_header.to_article(content, summary)
                    await article.save()
                    messages = await spread_message(bot, article)
                    if messages:
                        await Message.insert(*messages)
        except Exception:
            logger.exception("Error in periodic_scrap")
        await asyncio.sleep(ARTICLE_MINING_INTERVAL)


async def main():
    await asyncio.gather(periodic_pool(), periodic_scrap())


if __name__ == "__main__":
    asyncio.run(main())
