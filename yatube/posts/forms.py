from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            "text": "Текст",
            "group": "Группа",
            "image": "Картинка"
        }

        help_texts = {
            "text": "Текст нового поста",
            "group": "Группа, к которой будет относиться пост",
            "image": "Иллюстрация к посту"
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('post', 'author', 'text', 'created')
        labels = {
            "post": "Пост",
            "author": "Комментатор",
            "text": "Текст",
            "created": "Дата  комментария"
        }

        help_texts = {
            "text": "Текст нового поста",
            "group": "Группа, к которой будет относиться пост",
            "image": "Иллюстрация к посту"
        }
