from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import aiohttp

from src.bot import get_bot_n_dispatcher, spread_message
from src.constants import ARTICLE_MINING_INTERVAL
from src.data_models import AsyncSessionMaker, Database, create_db_engine_n_sessionmaker
from src.llm import query_summary
from src.pages import gen_article_ids, get_article_text, log_in

if TYPE_CHECKING:
    from aiogram import Bot


async def periodic_miner(
    db_session_maker: AsyncSessionMaker,
    bot: Bot,
) -> str:
    while True:
        async with aiohttp.ClientSession() as http_session:
            http_session = await log_in(http_session)

            # TODO: make synchronized for loop to define new articles and then use async to process them
            async for article_id in gen_article_ids(http_session, db_session_maker):
                article_text = await get_article_text(http_session, article_id)
                summary_text = await query_summary(article_text)
                await spread_message(bot, summary_text, db_session_maker)

        await asyncio.sleep(ARTICLE_MINING_INTERVAL)


async def main():
    db_engine, db_session_maker = create_db_engine_n_sessionmaker()
    async with db_engine.begin() as conn:
        await conn.run_sync(Database.metadata.drop_all)
        await conn.run_sync(Database.metadata.create_all)

    bot, dp = get_bot_n_dispatcher()

    asyncio.create_task(periodic_miner(db_session_maker, bot))
    await dp.start_polling(bot, db_session_maker=db_session_maker)


if __name__ == "__main__":
    asyncio.run(main())
