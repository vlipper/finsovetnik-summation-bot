from aiohttp import ClientSession
from bs4 import BeautifulSoup

from src.constants import HIDDEN_LOGIN_ATTRIBUTES, LOGIN_DATA, LOGIN_URL


def get_tag_value(
    soup: BeautifulSoup,
    tag_name: str,
    **attributes: dict[str, str],
) -> str:
    tag = soup.find(tag_name, attributes)
    if tag is None:
        raise ValueError(f"Tag '{tag_name}' is not found")

    value = tag.get("value")
    if value is None:
        raise ValueError(f"Tag '{tag_name}' does not have value")

    return value


async def session_login(session: ClientSession) -> ClientSession:
    async with session.get(LOGIN_URL) as response:
        if response.status != 200:
            raise Exception(f"Login page returned bad status: {response.status}")
        content = await response.text()

    # get hidden input attributes for login
    soup = BeautifulSoup(content, "html.parser")
    filled_attrs = {attr: get_tag_value(soup, "input", name=attr) for attr in HIDDEN_LOGIN_ATTRIBUTES}

    # send POST request to login
    login_data = LOGIN_DATA | filled_attrs
    async with session.post(LOGIN_URL, data=login_data) as _:
        pass

    return session
