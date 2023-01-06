# posts/tests/test_subscription.py
# test authorized user may subscribe and unsubscribe
def test_auth_subscribe_unsubscribe():
# создадим авторизованного - он подписывается , смотрит список постов, видит его
# отписывается, смотрит список постов -не получает список

# test new record appears only for subscribed users
def test_new_rec_for_unsubscribed_only ():
    self.assertIn(test_post, page_obj)
    self.assertNotIn(test_post, page_obj)
# создадим пост, создадим подписанного и неподписанного -
# нового поста нет в списке для неподписанного пользователя, для подписанного есть