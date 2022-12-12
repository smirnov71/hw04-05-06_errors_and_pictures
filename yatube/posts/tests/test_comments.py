import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django. core. cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Group, Post, Comment
from ..forms import PostForm
from datetime import date

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
SMALL_GIF = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B')

test_image = SimpleUploadedFile(
    name='small.gif',
    content=SMALL_GIF,
    content_type='image/gif')

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CommentTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user_creator = User.objects.create(username='user_cr')
        
        cls.comment = Comment.objects.create(
            text='Тестовый коммент',
            author=cls.user_creator,
            post=cls.post,
            created=date.today(),
        )
        cls.form_field = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Модуль shutil - библиотека Python с удобными инструментами 
        # для управления файлами и директориями: 
        # создание, удаление, копирование, перемещение, изменение папок и файлов
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)    

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_uncreator)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='first',
            description='Тестовая группа'
        )
        
        cache.clear()
        
    def test_profile_show_correct_context(self):
        """Изображение передаётся в словаре context."""

        pages_list = {
            'posts:index', {'username': self.post.author},
            'posts:profile', {'username': self.post.author},
            'posts:posts', {'username': self.post.author},
            'posts:post_detail', {'post_id': self.post.pk}
        }

        for name, kwargs in pages_list.items:
            response = self.authorized_client.get(reverse(name, kwargs))
            self.assertIn('image', response.context)

    def test_post_create(self):
        """Создание поста с картинкой создаёт запись в базе данных."""

        form_data = {
            'group': self.group.id,
            'text': 'Тестовый текст',
            'image': test_image,
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
        """Редактирование поста с картинкой создаёт запись в базе данных."""
        post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group,
            image=test_image,
        )
        new_post_text = 'new text'
        new_group = Group.objects.create(
            title='New Test group',
            slug='new-test-group',
            description='new test description'
        )

        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data={'text': new_post_text, 'group': new_group.id, 'image': test_image},
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
       