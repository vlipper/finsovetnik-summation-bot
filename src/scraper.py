import re
from collections.abc import AsyncIterator
from dataclasses import dataclass
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


def _get_start_dttm() -> datetime:
    table_exists = Article.exists().run_sync()
    if not table_exists:
        return datetime.now(UTC)

    max_posted_at = (
        Article.select(Article.posted_at).order_by(Article.posted_at, ascending=False).first().run_sync()
    )
    max_posted_at = max_posted_at["posted_at"]  # ty: ignore[not-subscriptable]
    return max_posted_at


START_DTTM = _get_start_dttm()


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
        msg = f"More than one tag matched selector: '{selector}' in tag: '{container.name}'"
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
        raise ValueError(  # noqa: TRY004
            f"Tag '{tag.name}' does not have attribute '{attr_name}'. Full tag:\n{tag}",
        )

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


async def gen_article_headers(http_session: ClientSession) -> AsyncIterator["ArticleHeader"]:
    async with http_session.get(ARTICLES_LIST_URL) as response:
        response.raise_for_status()
        content = await response.text()
    soup = BeautifulSoup(content, "html.parser")
    header_tags = _get_tags(soup, "article[id]")
    if len(header_tags) < CATCH_UP_ARTICLES:
        logger.warning(f"Found {len(header_tags)} articles, while {CATCH_UP_ARTICLES} expected")
    header_tags = header_tags[:CATCH_UP_ARTICLES][::-1]
    headers = [ArticleHeader.from_tag(t) for t in header_tags]
    for header in headers:
        # TODO: handle updates from here
        if header.posted_at > START_DTTM and not await header.is_stored():
            yield header


def extract_article_content(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    content_tag = _get_tag(soup, selector="article [class=entry-content]")
    # remove like button from article's content
    _get_tag(content_tag, selector="[class=llas-like-button-active]").decompose()

    return str(content_tag)


@dataclass
class ArticleHeader:
    article_id: int
    posted_at: datetime
    updated_at: datetime

    @classmethod
    def from_tag(
        cls,
        article_tag: Tag,
    ) -> "ArticleHeader":
        article_id = article_tag.get("id")
        if not isinstance(article_id, str) or not re.fullmatch(r"^post-\d+$", article_id):
            raise ValueError(f"Article id '{article_id}' is not valid. Full tag:\n{article_tag}")
        article_id = int(article_id[5:])

        posted_dttm = _get_attr(article_tag, selector="[class=entry-date]", attr_name="datetime")
        posted_dttm = datetime.fromisoformat(posted_dttm).astimezone(UTC)
        updated_dttm = _get_attr(article_tag, selector="[class=updated]", attr_name="datetime")
        updated_dttm = datetime.fromisoformat(updated_dttm).astimezone(UTC)

        return cls(article_id, posted_dttm, updated_dttm)

    async def is_stored(self) -> bool:
        return await Article.exists().where(Article.article_id == self.article_id)

    async def fetch_html(
        self,
        http_session: ClientSession,
    ) -> str:
        article_url = ARTICLE_TEMPLATE_URL.format(self.article_id)
        async with http_session.get(article_url) as response:
            response.raise_for_status()
            html = await response.text()

        return html

    def to_article(
        self,
        content_tag: str,
        summary: str,
    ) -> Article:
        return Article(
            article_id=self.article_id,
            posted_at=self.posted_at,
            updated_at=self.updated_at,
            content_tag=content_tag,
            summary=summary,
        )
