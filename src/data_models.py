from piccolo.columns import ForeignKey, Integer, OnDelete, Text, Timestamp
from piccolo.engine import SQLiteEngine
from piccolo.table import Table

from src.settings import DATABASE_PATH

DB = SQLiteEngine(path=DATABASE_PATH)


class Chat(Table, tablename="chats", db=DB):
    chat_id = Integer(primary_key=True)


class Article(Table, tablename="articles", db=DB):
    article_id = Integer(primary_key=True)
    posted_at = Timestamp(required=True)
    updated_at = Timestamp(required=True)
    content_tag = Text(required=True)
    summary = Text(required=True)


class Message(Table, tablename="messages", db=DB):
    message_id = Integer()
    chat_id = ForeignKey(Chat, on_delete=OnDelete.no_action)
    article_id = ForeignKey(Article, on_delete=OnDelete.no_action)
