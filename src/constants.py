import os

# general
ARTICLE_MINING_INTERVAL = 60 * 1  # 5 min
CATCH_UP_ARTICLES = 1
DATABASE_PATH = "./db/prod.sqlite"
BOT_TOKEN = os.environ["BOT_TOKEN"]

# URLs
ROOT_URL = "https://finsovetniksub.com/"
LOGIN_URL = f"{ROOT_URL}?page_id=13776"
ARTICLES_LIST_URL = f"{ROOT_URL}?page_id=1023"
ARTICLE_TEMPLATE_URL = f"{ROOT_URL}?p={{}}"

# login related
LOGIN_DATA = {"log": os.environ["SITE_USERNAME"], "pwd": os.environ["SITE_PASSWORD"]}
HIDDEN_LOGIN_ATTRIBUTES = ["ihcaction", "ihc_login_nonce"]

# llm related
MODEL_NAME = "gpt-5-mini"
SYSTEM_MESSAGE = """
Ты - помощник, который генерирует краткие аннотации к заметкам из блога "Финансовый советник".
Твоя задача - создать аннотацию размером не более 1024 символов, которая будет содержать основные мысли заметки.
Не добавляй в аннотацию ничего лишнего и не делай выводы.
Пиши аннотацию от лица автора, чтобы не тратить символы на вводные фразы.
Часто заметка может быть неполной или ссылаться на информацию, которой у тебя нет. Ты должен игнорировать эти огрехи.
""".strip()
