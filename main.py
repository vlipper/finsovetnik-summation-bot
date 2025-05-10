import asyncio

import aiohttp

from src.pages import session_login


async def main():
    async with aiohttp.ClientSession() as session:
        session = await session_login(session)
        pass


if __name__ == "__main__":
    asyncio.run(main())
