import os

# URLs
ROOT_URL = "https://finsovetniksub.com/"
LOGIN_URL = f"{ROOT_URL}?page_id=13776"
ARTICLES_LIST_URL = f"{ROOT_URL}?page_id=1023"
ARTICLE_TEMPLATE_URL = f"{ROOT_URL}?p={{}}"

# login related
LOGIN_DATA = {"log": os.environ["SITE_USERNAME"], "pwd": os.environ["SITE_PASSWORD"]}
HIDDEN_LOGIN_ATTRIBUTES = ["ihcaction", "ihc_login_nonce"]

NUM_ARTICLES_IN_LIST = 10

# llm related
MODEL_NAME = "gpt-4.1-nano"
SYSTEM_MESSAGE = """
Ты - помощник, который генерирует краткие аннотации к статьям из блога "Финансовый советник".
Ты должен отвечать только на русском языке.
Твоя задача - создать аннотацию размером не более 1024 символов, которая будет содержать основные идеи и выводы статьи.
Не добавляй в аннотацию ничего лишнего и не делай выводы, которые не содержатся в статье.
Часто статья может быть неполной или ссылаться на информацию, которой у тебя нет, но ты должен игнорировать эти огрехи.
""".strip()
