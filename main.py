from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import aiohttp

from src.bot import get_bot_n_dispatcher, spread_message
from src.constants import ARTICLE_MINING_INTERVAL
from src.llm import query_summary
from src.pages import gen_article_ids, get_article, log_in

if TYPE_CHECKING:
    from aiogram import Bot


async def periodic_miner(bot: Bot) -> str:
    while True:
        async with aiohttp.ClientSession() as http_session:
            http_session = await log_in(http_session)

            # TODO: make synchronized for loop to define new articles and then use async to process them
            async for article_id in gen_article_ids(http_session):
                article = await get_article(http_session, article_id)
                summary_text = await query_summary(article.text)
                await spread_message(bot, summary_text)
                await article.save()

        await asyncio.sleep(ARTICLE_MINING_INTERVAL)


async def main():
    bot, dp = get_bot_n_dispatcher()

    asyncio.create_task(periodic_miner(bot))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
