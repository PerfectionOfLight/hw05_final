from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Группа для теста'
        )
        cls.group = Group.objects.get(slug='test-group')

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        group = GroupModelTest.group
        field_verboses = {
            'title': 'Название сообщества',
            'slug': 'Slug-метка',
            'description': 'Описание сообщества',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        group = GroupModelTest.group
        field_help_texts = {
            'title': 'Введите название сообщества',
            'slug': 'Введите slug',
            'description': 'Введите описание сообщества',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    def test_object_name_is_title_fild(self):
        """В поле __str__  объекта group записано значение поля group.title."""
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User = get_user_model()
        cls.author = User.objects.create()
        Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Группа для теста'
        )
        cls.group = Group.objects.get(slug='test-group')
        Post.objects.create(
            text='Тестовый текст',
            author=cls.author,
            group=cls.group
        )
        cls.post = Post.objects.get(text='Тестовый текст')

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата опубликования',
            'author': 'Автор',
            'group': 'Сообщество',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст',
            'pub_date': 'Введите дату опубликования',
            'author': 'Укажите автора',
            'group': 'Укажите сообщество',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_object_name_is_title_fild(self):
        """__str__ в post возврящает ожидаемое"""
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(str(post), expected_object_name)
