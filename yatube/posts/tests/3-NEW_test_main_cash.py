# posts/tests/test_main_cash.py
# on main page record stored and refreshed every 20 seconds
# создадим тестовую запись  POST_00 на главной странице, через 10 сек изменим
# его на POST_10, a еще через 9 сек прочтём и сравним-не должно измениться
# ещё через 2 сек снова прочтём и сравним - должно измениться

from django.test import Client, TestCase
from posts.models import Group, Post, User
from django.urls import reverse
import time

class PostCache20(TestCase):
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

    def test_post_create(self):
        # Отправляем первый POST-запрос
        form_data = {
            'group': self.group.id,
            'text': 'test_00',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        time.sleep(18)
        # Отправляем второй POST-запрос
        form_data = {
            'group': self.group.id,
            'text': 'test_10',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        time.sleep(1)
        # Проверяем, совпадает ли текст
        self.assertEqual(
            response,
            reverse('posts:profile', kwargs={'username': self.user})
        )
