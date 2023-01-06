# posts/tests/test_comments.py
# only authorized users may leave a comment
from http import HTTPStatus
from posts.models import Comment, Post
from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()

class PostCreateFormTests(TestCase):
    def setUp(self):
        # Создаем авторизованный клиент
        self.user = User.objects.create(username='TestUser')
        self.unauth_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_auth_can_comment(self):
        """Авторизованнй может комментировать"""

        form_data = {
            'group': self.group.id,
            'text': 'Тестовый текст',
        }
        # Создаём пост
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Создаём комент
        comment_response = self.authorized_client.post(
            reverse('posts:add_comment'),
            data=form_data,
            follow=True
        )
        # Проверяем, увеличилось ли число коментов
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.first()
        self.assertEqual(comment.text, 'Теcтовый  коммент')
        self.assertEqual(comment.author, self.user)

    def test_unauth_cant_comment(self):
        """Неавторизованнй НЕ может комментировать"""
        comment_response = self.unauth_client.get(reverse('posts:add_comment'))
        self.assertEqual(comment_response.status_code, HTTPStatus.FOUND)
        