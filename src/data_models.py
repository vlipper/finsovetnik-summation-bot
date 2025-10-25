from piccolo.columns import Integer
from piccolo.engine import SQLiteEngine
from piccolo.table import Table

from src.constants import DATABASE_PATH

DB = SQLiteEngine(path=DATABASE_PATH)


class Chat(Table, tablename="chats", db=DB):
    chat_id = Integer(primary_key=True)


class Article(Table, tablename="articles", db=DB):
    article_id = Integer(primary_key=True)
