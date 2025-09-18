import databases
import ormar
import sqlalchemy

from src.constants import DATABASE_URL

base_ormar_config = ormar.OrmarConfig(
    database=databases.Database(DATABASE_URL),
    metadata=sqlalchemy.MetaData(),
    engine=sqlalchemy.create_engine(DATABASE_URL),
)


class Chat(ormar.Model):
    ormar_config = base_ormar_config.copy(tablename="chats")

    chat_id: int = ormar.Integer(primary_key=True, autoincrement=False)


class Article(ormar.Model):
    ormar_config = base_ormar_config.copy(tablename="articles")

    article_id: int = ormar.Integer(primary_key=True, autoincrement=False)
