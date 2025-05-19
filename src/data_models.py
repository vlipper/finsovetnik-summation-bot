from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.constants import DATABASE_URL

AsyncSessionMaker = async_sessionmaker[AsyncSession]


class Database(DeclarativeBase):
    pass


class Chat(Database):
    __tablename__ = "chats"

    chat_id: Mapped[int] = mapped_column(primary_key=True)


class Article(Database):
    __tablename__ = "articles"

    article_id: Mapped[int] = mapped_column(primary_key=True, index=True, unique=True)


def create_db_engine_n_sessionmaker() -> tuple[AsyncEngine, AsyncSessionMaker]:
    engine = create_async_engine(DATABASE_URL, echo=True)
    session_maker = async_sessionmaker(engine)

    return engine, session_maker
