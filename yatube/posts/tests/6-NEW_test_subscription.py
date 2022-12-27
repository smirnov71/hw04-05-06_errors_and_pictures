# posts/tests/test_subscription.py
# test authorized user may subscribe and unsubscribe
def test_auth_subscribe_unsubscribe():
# создадим авторизованного - он подписывается - получает список постов,
# отписывается -не получает список

# test new record appears only for subscribed users
def test_new_rec_for_unsubscribed_only ():
# создадим пост, создадим подписанного и неподписанного -
# неподписанный не увидит,подписанный увидит