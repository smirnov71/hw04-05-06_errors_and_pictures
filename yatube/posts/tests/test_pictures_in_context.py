from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django. core. cache import cache

from posts.models import Group, Post
from ..forms import PostForm
from datetime import date

User = get_user_model()


class PostPictureTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user_creator = User.objects.create(username='user_cr')

        cls.post = Post.objects.create(
            text='Тестовая запись для создания нового поста',
            author=cls.user_creator,
            group=cls.group,
            pub_date=date.today()
            image = {testimage.jpg}
        )
        cls.form_field = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField

        }


    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_uncreator)
        cache.clear()
        

    def test_profile_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:index', kwargs={'username': self.post.author}
        ))
        
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.post.author}
        ))

        response = self.authorized_client.get(reverse(
            'posts:posts', kwargs={'username': self.post.author}
        ))
        
        response = self.authorized_client.post(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}
        ))

        self.assertIn('image', response.context)
       