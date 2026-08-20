import re
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from logging import getLogger

from aiohttp import ClientSession
from bs4 import BeautifulSoup, Tag

from src.data_models import Article
from src.settings import (
    ARTICLE_TEMPLATE_URL,
    ARTICLES_LIST_URL,
    CATCH_UP_ARTICLES,
    HIDDEN_LOGIN_ATTRIBUTES,
    LOGIN_DATA,
    LOGIN_URL,
)

logger = getLogger(__name__)


def _get_tags(
    container: BeautifulSoup | Tag,
    selector: str,
) -> list[Tag]:
    tags = container.select(selector)
    if len(tags) == 0:
        raise ValueError(f"There are no tags matched selector: '{selector}'")

    return tags


def _get_tag(
    container: BeautifulSoup | Tag,
    selector: str,
    take_first: bool = True,
) -> Tag:
    tags = _get_tags(container, selector)
    if len(tags) > 1:
        msg = f"More than one tag matched selector: '{selector}'"
        if take_first:
            logger.info(f"{msg}. Taking the first one")
        else:
            raise ValueError(msg)

    return tags[0]

def _get_attr(
    tag: Tag,
    attr_name: str,
    selector: str | None = None,
) -> str:
    if selector:
        tag = _get_tag(tag, selector)
    attr = tag.get(attr_name)
    if not isinstance(attr, str):
        raise ValueError(f"Tag '{tag.name}' does not have attribute '{attr_name}'")  # noqa: TRY004

    return attr


async def log_in(http_session: ClientSession) -> ClientSession:
    # get hidden input attributes for login
    async with http_session.get(LOGIN_URL) as response:
        response.raise_for_status()
        content = await response.text()
    soup = BeautifulSoup(content, "html.parser")
    filled_attributes = {
        attr: _get_attr(soup, selector=f"input[name={attr}]", attr_name="value")
        for attr in HIDDEN_LOGIN_ATTRIBUTES
    }

    # send POST request to login
    login_data = LOGIN_DATA | filled_attributes
    async with http_session.post(LOGIN_URL, data=login_data) as response:
        # TODO: raise an error if a redirect happened
        response.raise_for_status()

    return http_session


async def gen_article_ids(http_session: ClientSession) -> AsyncIterator[int]:
    async with http_session.get(ARTICLES_LIST_URL) as response:
        response.raise_for_status()
        content = await response.text()
    soup = BeautifulSoup(content, "html.parser")
    article_ids = [t.get("id") for t in _get_tags(soup, "article[id]")]
    if len(article_ids) < CATCH_UP_ARTICLES:
        logger.warning(f"Found {len(article_ids)} articles, while {CATCH_UP_ARTICLES} expected")

    for article_id in article_ids[:CATCH_UP_ARTICLES]:
        if not isinstance(article_id, str) or not re.fullmatch(r"^post-\d+$", article_id):
            raise ValueError(f"Article id '{article_id}' is not valid")
        article_id = int(article_id[5:])
        # break if article is already in database
        article = await Article.select().where(Article.article_id == article_id).first()
        if article is not None:
            break

        yield article_id


async def get_article(
    http_session: ClientSession,
    article_id: int,
) -> Article:
    article_url = ARTICLE_TEMPLATE_URL.format(article_id)
    async with http_session.get(article_url) as response:
        response.raise_for_status()
        content = await response.text()

    soup = BeautifulSoup(content, "html.parser")
    article_tag = _get_tag(soup, selector="article")
    posted_dttm = _get_attr(article_tag, selector="header [class=entry-date]", attr_name="datetime")
    posted_dttm = datetime.fromisoformat(posted_dttm).astimezone(UTC)
    updated_dttm = _get_attr(article_tag, selector="header [class=updated]", attr_name="datetime")
    updated_dttm = datetime.fromisoformat(updated_dttm).astimezone(UTC)

    article = Article(article_id=int(article_id), posted_at=posted_dttm, updated_at=updated_dttm)
    article.text = str(article_tag)  # TODO: shitty trick

    return article
