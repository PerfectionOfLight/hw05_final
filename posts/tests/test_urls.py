from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.contrib.sites.models import Site

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test-user')
        cls.user_non_author = User.objects.create(
            username='test-user-2')
        cls.site = Site(pk=1, domain='localhost:8000', name='localhost:8000')
        cls.site.save()

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Группа для теста'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            pub_date='1969-1-1',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = PostURLTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.user_non_author = PostURLTests.user_non_author
        self.authorized_client_non_author = Client()
        self.authorized_client_non_author.force_login(self.user_non_author)

    def test_urls_exist_at_desired_location(self):
        """Страницы доступны любому пользователю."""
        url_names = (
            '/',
            '/group/test-group/',
            '/new/',
            '/test-user/',
            '/test-user/1/edit/',
        )
        for url in url_names:
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_new_redirect(self):
        """Страница /new/ перенаправляет анонимного пользователя."""
        response = self.guest_client.get('/new/',
                                         follow=True)
        self.assertRedirects(response, '/auth/login/?next=/new/')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'index.html',
            '/group/test-group/': 'group.html',
            '/new/': 'posts/new.html',
            '/test-user/1/edit/': 'posts/new.html',
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_edit(self):
        """Страица /test-user/1/edit/ перенаправляет анонимного
        пользователя."""
        response = self.guest_client.get(
            '/test-user/1/edit/',
            follow=True)
        self.assertRedirects(response, '/auth/login/?next=/test-user/1/edit/')

    def test_post_edit_non_author(self):
        """Страица /test-user/1/edit/ перенаправляет не автора."""
        response = self.authorized_client_non_author.get('/test-user/1/edit/',
                                                         follow=True)
        self.assertRedirects(response, '/test-user/1/')

    def test_post_edit_author(self):
        """Страица /test-user/1/edit/ доступна автору."""
        response = self.authorized_client.get('/test-user/1/edit/',
                                              follow=True)
        self.assertEqual(response.status_code, 200)

    def test_page_not_found(self):
        """Страица /page_not_found/ не найдена."""
        response = self.guest_client.get('/page_not_found/')
        self.assertEqual(response.status_code, 404)

    def test_add_comments(self):
        """Страица /test_User/1/comment доступна
        авторизованному пользователю."""
        response = self.authorized_client.get('/test-user/1/comment/')
        self.assertRedirects(response, '/test-user/1/')

    def test_add_comments_guest(self):
        """Страица /test_User/1/comment перенаправляет
        анонимного пользователя на вход."""
        response = self.guest_client.get('/test-user/1/comment/')
        self.assertRedirects(response,
                             '/auth/login/?next=/test-user/1/comment/')
