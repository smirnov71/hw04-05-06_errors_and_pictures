from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django. core. cache import cache

from posts.models import Group, Post, Follow
from ..forms import PostForm
from datetime import date

User = get_user_model()


class PostTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user_creator = User.objects.create(username='user_cr')
        cls.user_uncreator = User.objects.create(username='user_un')
        cls.group = Group.objects.create(
            title='Заголовок для тестовой группы',
            slug='test_slug',
            description='Текст описания тестовой группы'
        )
        cls.post = Post.objects.create(
            text='Тестовая запись для создания нового поста',
            author=cls.user_creator,
            group=cls.group,
            pub_date=date.today()
        )
        cls.form_field = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        cls.posts = cls.post.author.posts.select_related('author')
        cls.cnt_posts = cls.post.author.posts.count()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='guest')
        self.post_creator = Client()
        self.post_creator.force_login(self.user_creator)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_uncreator)

    def check_context_contains_page_or_post(self, context, post=False):
        if post:
            self.assertIn('post', context)
            post = context['post']
        else:
            self.assertIn('page', context)
            post = context['page'][0]
        self.assertEqual(post.author, PostTests.user_creator)
        self.assertEqual(post.pub_date, PostTests.post.pub_date)
        self.assertEqual(post.text, PostTests.post.text)
        self.assertEqual(post.group, PostTests.post.group)

    # def checking_correct_group(self, group):
    #     self.assertEqual(self.group.title, group.title)
    #     self.assertEqual(self.group.slug, group.slug)
    #     self.assertEqual(self.group.description, group.description)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse(
                'posts:index'
            ): 'posts/index.html',
            reverse(
                'posts:posts', kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': self.post.author}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.pk}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_create'
            ): 'posts/post_create.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.pk}
            ): 'posts/post_create.html',
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.post_creator.get(reverse_name)
                self.assertTemplateUsed(response, template)
                if reverse_name == reverse(
                    'posts:post_edit', kwargs={'post_id': self.post.pk}
                ):
                    self.assertRedirects(
                        self.guest_client.get(reverse_name),
                        '/auth/login/?next=%2Fposts%2F1%2Fedit%2F'
                    )
                elif reverse_name == reverse(
                    'posts:post_create',
                ):
                    self.assertRedirects(
                        self.guest_client.get(reverse_name),
                        '/auth/login/?next=%2Fcreate%2F'
                    )
                else:
                    self.assertTemplateUsed(
                        self.guest_client.get(reverse_name),
                        template
                    )

    def test_index_show_correct_context(self):
        "Список всех постов"
        response = self.authorized_client.get(reverse('posts:index'))
        self.check_context_contains_page_or_post(response.context)

    def test_grouplist_show_correct_context(self):
        """Список постов отфильтрованный по группе"""
        response = self.authorized_client.get(reverse(
            'posts:posts', kwargs={'slug': self.group.slug}
        ))
        self.check_context_contains_page_or_post(response.context.get('group'))
        self.check_context_contains_page_or_post(
            response.context['page_obj'][0], post=True
        )

    def test_profile_show_correct_context(self):
        "Список постов отфильтрованный по пользователю"
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.post.author}
        ))
        self.check_context_contains_page_or_post(response.context)

        self.assertIn('author', response.context)
        self.assertEqual(response.context['author'], PostTests.user)

    def test_postdetail_show_correct_context(self):
        """Один пост, отфильтрованный по id"""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}
        ))
        self.check_context_contains_page_or_post(response.context, post=True)

        self.assertIn('author', response.context)
        self.assertEqual(response.context['author'], PostTests.user_creator)

        self.assertIn('posts_count', response.context)
        self.assertEqual(
            response.context['posts_count'], PostTests.user.posts.count()
        )

    def test_add_or_editpost_show_correct_context(self):
        """Форма редактирования поста, отфильтрованного по id"""
        # Сначала проверка редактирования поста
        response = self.post_creator.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.pk}
        ))

        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertIn('is_edit', response.context)
        is_edit = response.context['is_edit']
        self.assertIsInstance(is_edit, bool)
        self.assertEqual(is_edit, True)

        # Теперь доп.проверка создания поста
        response = self.authorized_client.get(reverse('posts:post_create'))
        is_edit = response.context['is_edit']
        self.assertEqual(is_edit, False)

        for value, expected in self.form_field.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user_auth = User.objects.create(username='auth')
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Текст описания тестовой группы'
        )
        cls.some_posts = [
            Post(
                author=cls.user_auth,
                text=f'Тестовый пост{i}',
                group=cls.group
            )
            for i in range(15)
        ]
        Post.objects.bulk_create(cls.some_posts)
        cls.pages: tuple = (
            reverse('posts:index'),
            reverse('posts:profile',
                    kwargs={'username': f'{cls.user_auth.username}'}),
            reverse('posts:posts',
                    kwargs={'slug': f'{cls.group.slug}'}))

    def setUp(self):
        self.not_authorized = Client()
        self.unauthorized = Client()
        self.authorized = Client()
        self.authorized.force_login(self.user_auth)
        cache.clear()

    def test_correct_page_context_guest_client(self):
        """Проверка количества постов на страницах для гостя. """
        cache.clear()
        for page in self.pages:
            response_1page = self.not_authorized.get(page)
            response_2page = self.not_authorized.get(page + '?page=2')
            self.assertEqual(
                len(response_1page.context.get('page_obj')), 10
            )
            self.assertEqual(
                len(response_2page.context.get('page_obj')), 5
            )
            cache.clear()

        pagination = {
            1: 10,
            2: 5
        }

        for page_number, count in pagination.items():
            response = self.unauthorized.get(
                reverse('posts:index'), {'page': page_number}
            )
            self.assertEqual(
                len(response.context.get('page_obj')), count
            )

    def test_correct_page_context_auth_client(self):
        """Проверка количества постов на страницах для авторизованного."""
        cache.clear()
        for page in self.pages:
            response_1page = self.authorized.get(page)
            response_2page = self.authorized.get(page + "?page=2")
            self.assertEqual(
                len(response_1page.context.get('page_obj')), 10
            )
            self.assertEqual(
                len(response_2page.context.get('page_obj')), 5
            )
            cache.clear()


class CacheViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)
        cls.group = Group.objects.create(
            title='test_group',
            slug='test-slug',
            description='test_description'
        )
        cls.post = Post.objects.create(
            text='test_post',
            group=cls.group,
            author=cls.author
        )

    def test_cache_index(self):
        """Проверка хранения и очищения кэша для index."""
        response = CacheViewsTest.authorized_client.get(reverse('posts:index'))
        posts = response.content
        Post.objects.create(
            text='test_new_post',
            author=CacheViewsTest.author,
        )
        response_old = CacheViewsTest.authorized_client.get(
            reverse('index')
        )
        old_posts = response_old.content
        self.assertEqual(
            old_posts,
            posts,
            'Не возвращает кэшированную страницу.'
        )
        cache.clear()
        response_new = CacheViewsTest.authorized_client.get(reverse('posts:index'))
        new_posts = response_new.content
        self.assertNotEqual(old_posts, new_posts, 'Нет сброса кэша.')


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.author = User.objects.create_user(
            username='test_author'
        )
        cls.auth_author_client = Client()
        cls.auth_author_client.force_login(cls.author)

        cls.user_fol = User.objects.create_user(
            username='test_user_fol'
        )
        cls.authorized_user_fol_client = Client()
        cls.authorized_user_fol_client.force_login(
            cls.user_fol
        )

        cls.user_unfol = User.objects.create_user(
            username='test_user_unfol'
        )
        cls.authorized_user_unfol_client = Client()
        cls.authorized_user_unfol_client.force_login(
            cls.user_unfol
        )
        cls.group = Group.objects.create(
            title='test_group',
            slug='test-slug',
            description='test_description'
        )
        cls.post = Post.objects.create(
            text='test_post',
            group=cls.group,
            author=cls.author
        )

    def test_follow(self):
        """Тест работы подписки на автора."""
        client = FollowViewsTest.authorized_user_unfol_client
        user = FollowViewsTest.user_unfol
        author = FollowViewsTest.author
        client.get(
            reverse(
                'posts:profile_follow',
                args=[author.username]
            )
        )
        follower = Follow.objects.filter(
            user=user,
            author=author
        ).exists()
        self.assertTrue(
            follower,
            'Не работает подписка на автора'
        )

    def test_unfollow(self):
        """Тест работы отписки от автора."""
        client = FollowViewsTest.authorized_user_unfol_client
        user = FollowViewsTest.user_unfol
        author = FollowViewsTest.author
        client.get(
            reverse(
                'posts:profile_unfollow',
                args=[author.username]
            ),

        )
        follower = Follow.objects.filter(
            user=user,
            author=author
        ).exists()
        self.assertFalse(
            follower,
            'Не работает отписка от автора'
        )

    def test_new_author_post_for_follower(self):
        client = FollowViewsTest.authorized_user_fol_client
        author = FollowViewsTest.author
        group = FollowViewsTest.group
        client.get(
            reverse(
                'posts:profile_follow',
                args=[author.username]
            )
        )
        response_old = client.get(
            reverse('posts:follow_index')
        )
        old_posts = response_old.context.get(
            'page'
        ).object_list
        self.assertEqual(
            len(response_old.context.get('page').object_list),
            1,
            'Не загружается правильное колличество старых постов'
        )
        self.assertIn(
            FollowViewsTest.post,
            old_posts,
            'Старый пост не верен'
        )
        new_post = Post.objects.create(
            text='test_new_post',
            group=group,
            author=author
        )
        cache.clear()
        response_new = client.get(
            reverse('posts:follow_index')
        )
        new_posts = response_new.context.get(
            'page'
        ).object_list
        self.assertEqual(
            len(response_new.context.get('page').object_list),
            2,
            'Нету нового поста'
        )
        self.assertIn(
            new_post,
            new_posts,
            'Новый пост не верен'
        )

    def test_new_author_post_for_unfollower(self):
        client = FollowViewsTest.authorized_user_unfol_client
        author = FollowViewsTest.author
        group = FollowViewsTest.group
        response_old = client.get(
            reverse('posts:follow_index')
        )
        old_posts = response_old.context.get(
            'page'
        ).object_list
        self.assertEqual(
            len(response_old.context.get('page').object_list),
            0,
            'Не загружается правильное колличество старых постов'
        )
        self.assertNotIn(
            FollowViewsTest.post,
            old_posts,
            'Старый пост не должен загружаться'
        )
        new_post = Post.objects.create(
            text='test_new_post',
            group=group,
            author=author
        )
        cache.clear()
        response_new = client.get(
            reverse('posts:follow_index')
        )
        new_posts = response_new.context.get(
            'page'
        ).object_list
        self.assertEqual(
            len(response_new.context.get('page').object_list),
            0,
            'Новый пост не должен появляться'
        )
        self.assertNotIn(
            new_post,
            new_posts,
            'Новый пост не должен появляться'
        )
