from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')
        labels = {
            'group': _('Группа'),
            'text': _('Текст'),
            'image': _('Выберите картинку'),
        }

        help_texts = {
            'group': _('Придумайте название'),
            'text': _('Сообщите важную новость!'),
            'image': _('Загрузить картинку')
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
