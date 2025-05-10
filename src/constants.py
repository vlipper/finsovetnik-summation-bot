import os

# URLs
LOGIN_URL = "https://finsovetniksub.com/?page_id=13776"
ARTICLES_LIST_URL = "https://finsovetniksub.com/?page_id=1023"

LOGIN_DATA = {"log": os.getenv("SITE_USERNAME"), "pwd": os.getenv("SITE_PASSWORD")}
HIDDEN_LOGIN_ATTRIBUTES = ["ihcaction", "ihc_login_nonce"]
