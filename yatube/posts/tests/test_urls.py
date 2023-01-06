# posts/tests/test_urls.py
from posts.models import Post, Group
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
# from django.shortcuts import get_object_or_404
# from datetime import date
from http import HTTPStatus
from django.core.cache import cache

User = get_user_model()


class StaticURLTests(TestCase):
    def test_homepage(self):
        # Создаем экземпляр клиента
        guest_client = Client()
        # Делаем запрос к главной странице и проверяем статус (смок-тест)
        response = guest_client.get('/')
        # Утверждаем, что для прохождения теста код должен быть равен 200
        self.assertEqual(response.status_code, 200)


# ТЕСТ НА ПРАВИЛЬНОСТЬ ВЫЗЫВАЕМЫХ ШАБЛОНОВ
class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth_user')
        cls.group = Group.objects.create(
            title='test title',
            description='Test description',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            text='Test text', author=cls.user, group=cls.group
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = User.objects.create_user(username='HasNoName')
        # Создаем первый клиент
        self.authorized_client = Client()
        # Создаем второй клиент
        # self.authorized_client_2 = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(PostsURLTests.user)
        cache.clear()

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/post_create.html',
            '/create/': 'posts/post_create.html',
            '/unexisting_page/': 'core/404.html',
        }
        for address, template in templates_url_names.items():
            # АВТОРИЗОВАННЫЙ ПОЛЬЗОВАТЕЛЬ
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

            # ВТОРОЙ ПОЛЬЗОВАТЕЛЬ - ВСЁ, КРОМЕ РЕДАКТИРОВАНИЯ
            # with self.subTest(address=address):
                # response = self.authorized_client_2.get(address)
                # if address == f'/posts/{self.post.id}/edit/':
                # self.assertRedirects(response, 'posts/post_detail.html')
                # else:
                # self.assertTemplateUsed(response, template)

            # ГОСТЬ - ВСЁ, КРОМЕ РЕДАКТИРОВАНИЯ И СОЗДАНИЯ
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                if address == '/create/':
                    self.assertRedirects(
                        response, '/auth/login/?next=/create/')
                elif address == f'/posts/{self.post.id}/edit/':
                    self.assertRedirects(
                        response,
                        f'/auth/login/?next=/posts/{self.post.id}/edit/')
                else:
                    self.assertTemplateUsed(response, template)

    #  НЕСУЩЕСТВУЮЩАЯ СТРАНИЦА - 404
    def test_unexisting_page(self):
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
