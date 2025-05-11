import os

# URLs
ROOT_URL = "https://finsovetniksub.com/"
LOGIN_URL = f"{ROOT_URL}?page_id=13776"
ARTICLES_LIST_URL = f"{ROOT_URL}?page_id=1023"
ARTICLE_TEMPLATE_URL = f"{ROOT_URL}?p={{}}"

# login related
LOGIN_DATA = {"log": os.getenv("SITE_USERNAME"), "pwd": os.getenv("SITE_PASSWORD")}
HIDDEN_LOGIN_ATTRIBUTES = ["ihcaction", "ihc_login_nonce"]

NUM_ARTICLES_IN_LIST = 10
