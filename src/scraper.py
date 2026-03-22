import re
from datetime import datetime, timezone
from typing import AsyncIterator

from aiohttp import ClientSession
from bs4 import BeautifulSoup, PageElement

from src.data_models import Article
from src.settings import (
    ARTICLE_TEMPLATE_URL,
    ARTICLES_LIST_URL,
    CATCH_UP_ARTICLES,
    HIDDEN_LOGIN_ATTRIBUTES,
    LOGIN_DATA,
    LOGIN_URL,
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


async def log_in(http_session: ClientSession) -> ClientSession:
    async with http_session.get(LOGIN_URL) as response:
        response.raise_for_status()
        content = await response.text()

    # get hidden input attributes for login
    soup = BeautifulSoup(content, "html.parser")
    filled_attributes = {
        attr: _get_tag_attribute(soup, "input", "value", name=attr)[1] for attr in HIDDEN_LOGIN_ATTRIBUTES
    }

    # send POST request to login
    login_data = LOGIN_DATA | filled_attributes
    async with http_session.post(LOGIN_URL, data=login_data) as response:
        # TODO: raise an error if a redirect happened
        response.raise_for_status()

    return http_session


async def gen_article_ids(http_session: ClientSession) -> AsyncIterator[str]:
    async with http_session.get(ARTICLES_LIST_URL) as response:
        response.raise_for_status()
        content = await response.text()

    page_element = BeautifulSoup(content, "html.parser")
    for _ in range(CATCH_UP_ARTICLES):
        page_element, article_id = _get_tag_attribute(page_element, "article", "id", id=True)

        # validate article id with regex
        if not re.fullmatch(r"^post-\d+$", article_id):
            raise ValueError(f"Article id '{article_id}' is not valid")
        article_id = int(article_id[5:])

        # check if article_id is already in the database
        article = await Article.select().where(Article.article_id == article_id).first()
        if article is not None:
            break

        yield article_id


async def get_article(
    http_session: ClientSession,
    article_id: str,
) -> Article:
    article_url = ARTICLE_TEMPLATE_URL.format(article_id)
    async with http_session.get(article_url) as response:
        response.raise_for_status()
        content = await response.text()

    soup = BeautifulSoup(content, "html.parser")
    content_tag = soup.find(attrs={"class": "entry-content"})
    text = content_tag.get_text("\n", strip=True)

    updated_tag = soup.find("time", attrs={"class": "updated"})
    updated_dttm = datetime.fromisoformat(updated_tag["datetime"]).astimezone(timezone.utc)

    article = Article(article_id=int(article_id), updated_at=updated_dttm)
    article.text = text  # TODO: shitty trick

    return article
