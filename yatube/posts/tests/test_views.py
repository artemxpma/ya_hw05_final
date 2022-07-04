# This Python file uses the following encoding: utf-8
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.conf import settings
from django import forms

from ..models import Group, Post, Comment, Follow
from .utils import post_body_test, view_bundle, reverse_ad, uploaded_img, get_follow_model


User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Тестовый пользователь')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='1',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=uploaded_img
        )
        cls.INDEX = ('posts/index.html',
                     ('posts:index',))
        cls.GROUP = ('posts/group_list.html',
                     ('posts:group_posts', [f'{cls.group.slug}']))
        cls.PROFILE = ('posts/profile.html',
                       ('posts:profile', [f'{cls.user.username}']))
        cls.POST = ('posts/post_detail.html',
                    ('posts:post_detail', [f'{cls.post.id}']))
        cls.CREATE = ('posts/create_post.html',
                      ('posts:post_create',))
        cls.EDIT = ('posts/create_post.html',
                    ('posts:post_edit', [f'{cls.post.id}']))
        cls.addresses = (
            cls.INDEX,
            cls.GROUP,
            cls.PROFILE,
            cls.POST,
            cls.CREATE,
            cls.EDIT
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адреса используют правильные шаблоны."""
        for template, address in self.addresses:
            with self.subTest():
                reverse_name = reverse_ad(*address)
                response = self.authorized_client.\
                    get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse_ad(*self.INDEX[1]))
        bundle = view_bundle(self, response.context['page_obj'][0])
        post_body_test(self, bundle)

    def test_group_posts_show_correct_context(self):
        """Шаблоны group_posts, сформированы с правильным контекстом."""
        response = self.authorized_client.get(
            reverse_ad(*self.GROUP[1]))
        bundle = view_bundle(self, response.context['page_obj'][0],
                             response.context['group'].title, self.group.title)
        post_body_test(self, bundle)

    def test_profile_show_correct_context(self):
        """Шаблоны profile, сформированы с правильным контекстом."""
        response = self.authorized_client.get(
            reverse_ad(*self.PROFILE[1]))
        bundle = view_bundle(self, response.context['page_obj'][0],
                             response.context['author_object'].username,
                             self.user.username)
        post_body_test(self, bundle)

    def test_post_detail_show_correct_context(self):
        """Шаблоны post_detail, сформированы с правильным контекстом."""
        POSTS_OF_SAME_AUTHOR = 1
        response = self.authorized_client.get(
            reverse_ad(*self.POST[1]))
        bundle = view_bundle(self, response.context['post'],
                             response.context['count'], POSTS_OF_SAME_AUTHOR)
        post_body_test(self, bundle)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse_ad(*self.CREATE[1]))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse_ad(*self.EDIT[1]))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_detail_show_comment(self):
        """Шаблон post_detail показывает комментарии."""
        comment = Comment.objects.create(
            author=self.user,
            post=self.post,
            text='Тестовый комментарий'
        )
        response = self.authorized_client.get(
            reverse_ad(*self.POST[1]))
        self.assertEqual(response.context['comments'].first(), comment)

    def test_index_cache(self):
        """Главная страница кэшируется"""
        response_first = self.authorized_client.get(reverse_ad(*self.INDEX[1]))
        Post.objects.create(
            author=self.user,
            text='пост для проверки кэша',
        )
        response_second = self.authorized_client.get(
            reverse_ad(*self.INDEX[1])
        )
        self.assertEqual(response_first.content,
                         response_second.content)
        cache.clear()
        response_after_clear = self.authorized_client.get(
            reverse_ad(*self.INDEX[1])
        )
        self.assertNotEqual(response_first.content,
                            response_after_clear.content)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Тестовый пользователь')
        cls.posts = [Post.objects.create(
            author=cls.user,
            text=f'Тестовый пост {i}'
        ) for i in range(13)]

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        '''Проверит количество постов на первой странице.'''
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        '''Проверит количество постов на второй странице.'''
        response = self.authorized_client.get(reverse(
            'posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)


class SubscribeViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create(username='Ползьователь на которого подписались')
        cls.user_follower = User.objects.create(username='Пользователь который подписался')
        cls.user_no_follow = User.objects.create(username='Пользователь не подписан ни на кого')
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Тестовый пост',
        )

    def setUp(self):
        self.auth_author = Client()
        self.auth_author.force_login(self.user_author)
        self.auth_follower = Client()
        self.auth_follower.force_login(self.user_follower)
        self.auth_no_follow = Client()
        self.auth_no_follow.force_login(self.user_no_follow)

    def test_user_can_subscribe_and_unsubscribe(self):
        '''Пользователь может подписаться и отписаться от автора.'''
        self.assertFalse(get_follow_model(self))
        self.auth_follower.get(reverse('posts:profile_follow', kwargs={'username': self.user_author.username}))
        self.assertTrue(get_follow_model(self))
        self.auth_follower.get(reverse('posts:profile_unfollow', kwargs={'username': self.user_author.username}))
        self.assertFalse(get_follow_model(self))

    def test_user_sees_who_follows(self):
        '''Пользователь видит посты тех, на кого подписан и не видит тех, накого не подписан'''