# posts/tests/test_cash.py
# erased post remains in response.content until cleared
# создаём запись в базе, стираем запись, проверяем 
# response.content главной страницы на ее наличие

from django.test import Client, TestCase
from posts.models import Group, Post, User
from django.urls import reverse

class TestCache(TestCase):
    def setUp(self):
        # Создаем авторизованный клиент
        self.user = User.objects.create(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='first',
            description='Тестовая группа'
        )


# альтернативная версия

    def test_index_cache(self):

        response  = self.uthorized_client.get(reverse('posts:index'))
        page_obj_before = response.context.get(page_obj)
        self.assertEqual(len(page_obj_before), 1)
        post= Post.objects.create(
            author= 'author',
            text= 'lorem ipsum'  
        )
        response_after = self.authorized_client.get(reverse('posts:index'))
        page_obj_before = response_after.context.get(page_obj)
        self.assertNotIn(post, page_obj)