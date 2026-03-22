import asyncio
import logging

import aiohttp
from aiogram import Bot

from src.bot import dp, spread_message
from src.llm import query_summary
from src.scraper import gen_article_ids, get_article, log_in
from src.settings import ARTICLE_MINING_INTERVAL, BOT_POOLING_INTERVAL, BOT_TOKEN

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
                async for article_id in gen_article_ids(http_session):
                    article = await get_article(http_session, article_id)
                    summary_text = await query_summary(article.text)
                    await spread_message(bot, summary_text)
                    await article.save()
        except Exception:
            logger.exception("Error in periodic_scrap")
        await asyncio.sleep(ARTICLE_MINING_INTERVAL)


async def main():
    await asyncio.gather(periodic_pool(), periodic_scrap())


if __name__ == "__main__":
    asyncio.run(main())
