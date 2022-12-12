from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.
User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField(
        'Текст поста',
        help_text='Текст нового поста'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add =True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='posts',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        help_text='Группа, к которой будет относиться пост',
        verbose_name='Группа'
    )
        # Поле для картинки (необязательное) 
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )  
    # Аргумент upload_to указывает директорию, 
    # в которую будут загружаться пользовательские файлы. 

    def __str__(self):
        return self.text[:15] 

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        help_text='Ccылка на пост',
        related_name='comments',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name='comments',
        on_delete=models.CASCADE,
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Текст комментария',
    )
    created = models.DateTimeField('Дата комментария', auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        help_text='Кто подписывается',
        related_name='follower',
        on_delete=models.CASCADE,
    
    )
    author = models.ForeignKey(
        User,
        help_text='На кого подписывается',
        related_name='following',
        on_delete=models.CASCADE,
    )
