# posts/tests/tests_form.py
import tempfile
from http import HTTPStatus
from posts.models import Group, Post
from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse

User = get_user_model()

# Создаем временную папку для медиа-файлов;
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


# Для сохранения media-файлов в тестах будет использоваться
# временная папка TEMP_MEDIA_ROOT, а потом мы ее удалим
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    def setUp(self):
        # Создаем авторизованный клиент
        self.user = User.objects.create(username='TestUser')
        self.unauth_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='first',
            description='Тестовая группа'
        )

    def test_post_create(self):
        """Валидная форма создает запись в Post."""

        form_data = {
            'group': self.group.id,
            'text': 'Тестовый текст',
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user})
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.text, 'Тестовый текст')
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, self.group)

    def test_post_edit(self):
        post = Post.objects.create(
            text='test',
            author=self.user,
            group=self.group
        )
        new_post_text = 'new text'
        new_group = Group.objects.create(
            title='New Test group',
            slug='new-test-group',
            description='new test description'
        )

        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data={'text': new_post_text, 'group': new_group.id},
            follow=True,
        )

        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.text, new_post_text)
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, new_group)

        old_group_response = self.authorized_client.get(
            reverse('posts:posts', args=(self.group.slug,))
        )

        self.assertEqual(
            old_group_response.context['page_obj'].paginator.count, 0
        )

    def test_unauth_user_cant_publish_post(self):
        response = self.unauth_client.post(reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
