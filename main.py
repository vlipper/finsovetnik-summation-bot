import asyncio

import aiohttp

from src.pages import gen_article_ids, get_page_text, session_login


async def main():
    async with aiohttp.ClientSession() as session:
        session = await session_login(session)
        async for article_id in gen_article_ids(session):
            article_text = await get_page_text(session, article_id)
            pass


if __name__ == "__main__":
    asyncio.run(main())
