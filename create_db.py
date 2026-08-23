from piccolo.table import create_db_tables_sync

from src.data_models import Article, Chat, Message

if __name__ == "__main__":
    create_db_tables_sync(Chat, Article, Message)
