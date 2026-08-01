import os

# general
DATABASE_PATH = "./db/prod.sqlite"

# bot
BOT_TOKEN = os.environ["BOT_TOKEN"]
BOT_POOLING_INTERVAL = 60  # 1 min

# scraper
ARTICLE_MINING_INTERVAL = 60 * 5  # 5 min
CATCH_UP_ARTICLES = 1

# URLs
ROOT_URL = "https://finsovetniksub.com/"
LOGIN_URL = f"{ROOT_URL}?page_id=13776"
ARTICLES_LIST_URL = f"{ROOT_URL}?page_id=1023"
ARTICLE_TEMPLATE_URL = f"{ROOT_URL}?p={{}}"

# login
LOGIN_DATA = {"log": os.environ["SITE_USERNAME"], "pwd": os.environ["SITE_PASSWORD"]}
HIDDEN_LOGIN_ATTRIBUTES = ["ihcaction", "ihc_login_nonce"]

# llm
MODEL_NAME = "openrouter/qwen/qwen3.7-plus"
SYSTEM_MESSAGE = """
Ты - помощник, который генерирует краткие аннотации к заметкам из блога "Финансовый советник".
Твоя задача - создать аннотацию размером не более 1024 символов, которая будет содержать основные мысли заметки.
Заметку пришлет пользователь в формате html.
Начни аннотацию с заголовка заметки.
Не добавляй в аннотацию ничего за рамками заметки и не делай выводы.
Пиши аннотацию от лица автора. Не трать символы на речевые обороты, не содержащие смысловой нагрузки.
Заметка может содержать недоступные ссылки или ссылаться на информацию, которой у тебя нет. Ты должен игнорировать эту неполноту или сообщить, если считаешь что недостающая информация критически важна.
""".strip()
