import tempfile
from django import forms
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import Client
from django.contrib.sites.models import Site
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from posts.models import Group, Post

User = get_user_model()


class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=tempfile.gettempdir())
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create(username='test-user')
        cls.site = Site(pk=1, domain='localhost:8000', name='localhost:8000')
        cls.site.save()
        cls.group0 = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description="Это тестовая группа",
        )
        cls.group_wrong = Group.objects.create(
            title='Другая тестовая группа',
            slug='wrong-group',
            description='В этой группе не должно быть постов',
        )
        Post.objects.bulk_create([Post(
            text=f'Тестовый пост {i}',
            author=cls.user,
            group=cls.group0,
            image = cls.uploaded
        ) for i in range(2)
        ])

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'index.html': reverse('posts:index'),
            'group.html': (reverse(
                'posts:group', kwargs={'slug': 'test-group'})),
            'posts/new.html': reverse('posts:new_post'),
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_main_page_show_correct_context(self):
        """View-функция главной страницы передает нужный контекст"""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(list(response.context.get('paginator').object_list),
                         list(Post.objects.order_by('-pub_date').all()))

    def test_group_page_show_correct_context(self):
        """View-функция страницы группы передает нужный контекст"""
        response = self.authorized_client.get(
            reverse('posts:group', args=['test-group'])
        )
        self.assertEqual(response.context.get('group'),
                         PostViewTests.group0)
        self.assertEqual(list(response.context.get('paginator').object_list),
                         list(PostViewTests.group0.posts.all()))

    def test_new_post_form_correct_context(self):
        """Поля формы создания нового поста передают нужные контексты"""
        response = self.authorized_client.get(reverse('posts:new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for field_name, field_format in form_fields.items():
            with self.subTest(value=field_name):
                form_field = (
                    response.context.get('form').fields.get(field_name)
                )
                self.assertIsInstance(form_field, field_format)

    def test_home_group_pages_show_created_post(self):
        """При указании группы новый пост появился на главной странице и
        странице группы."""
        post = Post.objects.create(
            text='test text ',
            author=PostViewTests.user,
            group=PostViewTests.group0
        )
        reverse_names_list = (
            (reverse('posts:index')),
            (reverse('posts:group', kwargs={'slug': 'test-group'})),
        )
        for reverse_name in reverse_names_list:
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(response.context.get('page')[0],
                                 post)

    def test_profile_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'test-user'}))
        self.assertEqual(response.context.get('count'),
                         len(Post.objects.all()))
        self.assertEqual(response.context.get('user_name'), PostViewTests.user)
        self.assertEqual(list(response.context.get('paginator').object_list),
                         list(PostViewTests.user.posts.all()))

    def test_post_edit_show_correct_context(self):
        """Шаблон edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'username': 'test-user', 'post_id': 1}))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
            'image': forms.fields.ImageField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
        self.assertIsInstance(form_field, expected)

    def test_post_show_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post',
            kwargs={'username': 'test-user', 'post_id': 1}))
        post = response.context['post']
        self.assertEqual(response.context.get('user_name'),
                         PostViewTests.user)
        self.assertEqual(response.context.get('count'),
                         len(Post.objects.all()))
        self.assertEqual(post,
                         Post.objects.get(pk=1))

    def test_cache(self):
        """При удалении поста кэш не меняется"""
        response = self.authorized_client.get(reverse('posts:index')).content
        Post.objects.get(pk=1).delete()
        response_after_delete = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertEqual(response, response_after_delete)
