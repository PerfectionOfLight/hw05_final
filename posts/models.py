from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(verbose_name="Название сообщества",
                             help_text="Введите название сообщества",
                             max_length=200)
    slug = models.SlugField(verbose_name="Slug-метка",
                            help_text="Введите slug",
                            max_length=200, unique=True)
    description = models.TextField(verbose_name="Описание сообщества",
                                   help_text="Введите описание сообщества")

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name='Текст', help_text='Введите текст')
    pub_date = models.DateTimeField(verbose_name='Дата опубликования',
                                    help_text='Введите дату опубликования',
                                    auto_now_add=True)
    author = models.ForeignKey(User, verbose_name='Автор',
                               help_text='Укажите автора',
                               on_delete=models.CASCADE,
                               related_name='posts')
    group = models.ForeignKey(Group, verbose_name='Сообщество',
                              help_text='Укажите сообщество',
                              blank=True, null=True,
                              on_delete=models.SET_NULL,
                              related_name='posts')
    image = models.ImageField(upload_to='posts/', blank=True, null=True,
                              verbose_name='Картинка к посту',
                              help_text='Загрузить картинку')

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey('Post',
                             on_delete=models.CASCADE,
                             related_name='comments',
                             verbose_name="Пост",
                             help_text="К какому посту относиться комментарий")
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="comments",
                               verbose_name="Автор",
                               help_text="Автор комментария")
    text = models.TextField(verbose_name="Текст",
                            help_text="Текст комментария")
    created = models.DateTimeField(verbose_name="Дата публикации",
                                   auto_now_add=True,
                                   help_text="Автоматически заполняется"
                                             "сегодняшней датой")


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='Подписчик',
                             help_text='Подписчик')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following',
                               verbose_name='Автор',
                               help_text='Подписка на')

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'author'],
                                               name='unique_follow')]
