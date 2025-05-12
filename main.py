import asyncio

import aiohttp

from src.llm import query_summary
from src.pages import gen_article_ids, get_page_text, session_login


async def main():
    async with aiohttp.ClientSession() as session:
        session = await session_login(session)
        # TODO: make synchronized for loop to define new articles and then use async to process them
        async for article_id in gen_article_ids(session):
            article_text = await get_page_text(session, article_id)
            summary_text = await query_summary(article_text)
            pass


if __name__ == "__main__":
    asyncio.run(main())
