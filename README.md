# finsovetnik-summation-bot

## plan
- save article text to db to compare it with updated text
    - maybe it's needed to take only the next tag: '<div class="entry-content">'
    - remove likes from tree with `https://beautiful-soup-4.readthedocs.io/en/latest/#extract`
- work with exceptions:
    - now exception logged. If article is broken, it will be processed again and again
    - maybe send message to personal chat
- add possibility to have a chat if user answered to bot's message
