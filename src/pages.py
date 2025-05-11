import re
from typing import AsyncIterator

from aiohttp import ClientSession
from bs4 import BeautifulSoup, PageElement

from src.constants import (
    ARTICLE_TEMPLATE_URL,
    ARTICLES_LIST_URL,
    HIDDEN_LOGIN_ATTRIBUTES,
    LOGIN_DATA,
    LOGIN_URL,
    NUM_ARTICLES_IN_LIST,
)


def _get_tag_attribute(
    page_element: PageElement,
    tag_name: str,
    attribute: str,
    **filter_attributes: dict[str, str],
) -> tuple[PageElement, str]:
    tag = page_element.find_next(tag_name, filter_attributes)
    if tag is None:  # TODO: shitty trick, but I don't know how to do it better
        tag = page_element.find(tag_name, filter_attributes)

    if tag is None:
        raise ValueError(f"Tag '{tag_name}' is not found")

    value = tag.get(attribute)
    if value is None:
        raise ValueError(f"Tag '{tag_name}' does not have attribute '{attribute}'")

    return tag, value


async def session_login(session: ClientSession) -> ClientSession:
    async with session.get(LOGIN_URL) as response:
        response.raise_for_status()
        content = await response.text()

    # get hidden input attributes for login
    soup = BeautifulSoup(content, "html.parser")
    filled_attributes = {
        attr: _get_tag_attribute(soup, "input", "value", name=attr)[1] for attr in HIDDEN_LOGIN_ATTRIBUTES
    }

    # send POST request to login
    login_data = LOGIN_DATA | filled_attributes
    async with session.post(LOGIN_URL, data=login_data) as response:
        # TODO: raise an error if a redirect happened
        response.raise_for_status()

    return session


async def gen_article_ids(session: ClientSession) -> AsyncIterator[str]:
    async with session.get(ARTICLES_LIST_URL) as response:
        response.raise_for_status()
        content = await response.text()

    page_element = BeautifulSoup(content, "html.parser")
    for _ in range(NUM_ARTICLES_IN_LIST):
        page_element, article_id = _get_tag_attribute(page_element, "article", "id", id=True)
        # validate article id with regex
        if not re.fullmatch(r"^post-\d+$", article_id):
            raise ValueError(f"Article id '{article_id}' is not valid")
        article_id = article_id[5:]

        yield article_id


async def get_page_text(
    session: ClientSession,
    article_id: str,
) -> str:
    article_url = ARTICLE_TEMPLATE_URL.format(article_id)
    async with session.get(article_url) as response:
        response.raise_for_status()
        content = await response.text()

    soup = BeautifulSoup(content, "html.parser")
    content_tag = soup.find(attrs={"class": "entry-content"})
    article_text = content_tag.get_text("\n", strip=True)

    return article_text
