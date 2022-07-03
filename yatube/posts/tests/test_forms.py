import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings

from ..models import Post, Group, Comment
from ..forms import PostForm
from .utils import post_body_test, uploaded_img


User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


def make_bundle(self, form_data, test_post):
    '''
    Принимает данные setUp, содержимое формы и проверяемый пост и
    компанует кортежи для проверки.
    '''
    return zip([test_post.text, test_post.group.pk, test_post.author],
               [form_data['text'], form_data['group'], self.user])


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Тестовый пользователь')
        cls.form = PostForm()
        cls.group_1 = Group.objects.create(
            title='Тестовая группа',
            slug='1',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='2',
            description='Тестовое описание 2',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create(self):
        """Валидная форма создает запись Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group_1.pk,
            'image': uploaded_img,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': f'{self.user.username}'}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post_body_test(self,
                       make_bundle(self, form_data, Post.objects.first()))

    def test_post_edit(self):
        """Валидная форма изменяет запись Post."""
        post = Post.objects.create(
            author=self.user,
            text='test text',
        )
        posts_count = Post.objects.count()
        form_data = {
            'text': 'test text after edit',
            'group': self.group_2.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': f'{post.id}'}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': f'{post.id}'}))
        self.assertEqual(Post.objects.count(), posts_count)
        post_body_test(self,
                       make_bundle(self, form_data, Post.objects.first()))

    def test_guest_create_post(self):
        '''Неавторизованный пользователь не может создать пост.'''
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group_1.pk,
        }
        response = self.guest.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse('users:login') + '?next=/create/')
        self.assertEqual(Post.objects.count(), posts_count)


class CommentFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Тестовый пользователь')
        cls.form = PostForm()
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest = Client()

    def test_guest_add_comment(self):
        '''Неавторизованный пользователь не может добавить комментарий.'''
        comments_count = Comment.objects.count()
        form_data = {
            'author': self.user,
            'post': self.post,
            'text': 'Тестовый комментарий'
        }
        response = self.guest.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('users:login') + '?next=/posts/1/comment/'
        )
        self.assertEqual(Comment.objects.count(), comments_count)
