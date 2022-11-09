from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        labels = {"text": "Текст", "group": "Группа", "image": "Картинка"}
        model = Post
        fields = ('text', 'group', 'image')
        help_texts = {
            "text": "Текст нового поста",
            "group": "Группа, к которой будет относиться пост",
            "image": "Иллюстрация к посту"
        }
