# finsovetnik-summation-bot

## plan
- compare texts if updated_at has modified: `content_tag.get_text(' ', True)`
    - compare hash values, then text lenghts with perc. threshold
- add possibility to have a chat if user answered to bot's message
- work with exceptions:
    - now exception logged. If article is broken, it will be processed again and again
    - maybe send message to personal chat
