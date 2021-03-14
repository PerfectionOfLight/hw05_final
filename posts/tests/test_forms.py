import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from posts.forms import PostForm
from posts.models import Group, Post


class FormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=tempfile.gettempdir())
        cls.user = get_user_model().objects.create(username='test-user')

        cls.group = Group.objects.create(
            title='test_group',
            slug='test',
            description='test_group'
        )

        cls.post = Post.objects.create(
            text='test text 1234556788888888888',
            author=cls.user,
            group=cls.group
        )
        cls.form = PostForm()

    def setUp(self):
        self.user = FormsTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_new_post(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        form_data = {
            'group': FormsTests.group.pk,
            'text': 'test text'
        }
        response = self.authorized_client.post(
            reverse('posts:new_post'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(Post.objects.latest('pk').text, form_data['text'])
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(response.status_code, 200)

    def test_edit_changes_post(self):
        """Валидная форма изменяет запись в Post."""
        small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                     b'\x01\x00\x80\x00\x00\x00\x00\x00'
                     b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                     b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                     b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                     b'\x0A\x00\x3B')
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        post_count = Post.objects.count()
        form_data = {
            'group': FormsTests.group.pk,
            'text': 'post edit',
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'username': 'test-user',
                            'post_id': FormsTests.post.pk}),
            data=form_data,
            follow=True
        )
        FormsTests.post.refresh_from_db()
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(form_data['text'], FormsTests.post.text)
        self.assertRedirects(response, reverse(
            'posts:post',
            kwargs={'username': 'test-user', 'post_id': FormsTests.post.pk}))
        self.assertEqual(response.status_code, 200)
