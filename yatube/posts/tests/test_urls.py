# This Python file uses the following encoding: utf-8
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post


User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Тест пользователь')
        cls.user_author = User.objects.create_user(username='Тест автор')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='1',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Тестовый пост',
        )
        cls.INDEX = ('/', 'posts/index.html')
        cls.GROUP = (f'/group/{cls.group.slug}/', 'posts/group_list.html')
        cls.PROFILE = (f'/profile/{cls.user.username}/', 'posts/profile.html')
        cls.POST = (f'/posts/{cls.post.id}/', 'posts/post_detail.html')
        cls.CREATE = ('/create/', 'posts/create_post.html')
        cls.EDIT = (f'/posts/{cls.post.id}/edit/', 'posts/create_post.html')
        cls.COMMENT = (f'/posts/{cls.post.id}/comment/',)
        cls.guest_addresses = (
            cls.INDEX,
            cls.GROUP,
            cls.PROFILE,
            cls.POST
        )
        cls.auth_addresses = (
            cls.CREATE,
            cls.EDIT
        )

    def setUp(self):
        self.guest = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user_author)

    def test_urls_uses_correct_template(self):
        '''Проверит, что страницы используют правильные шаблоны.'''
        for address, template in (*self.guest_addresses, *self.auth_addresses):
            with self.subTest(address=address):
                response = self.authorized_client_author.get(address)
                self.assertTemplateUsed(response, template)

    def test_url_works_as_desired_for_guest(self):
        """Страницы доступны гостю."""
        for address, _ in self.guest_addresses:
            with self.subTest():
                response = self.guest.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url_works_as_desired_for_guest(self):
        """Страница create перенаправляет гостя."""
        response = self.guest.get(self.CREATE[0])
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_edit_url_works_as_desired_for_guest(self):
        """Страница edit перенаправляет гостя."""
        response = self.guest.get(self.EDIT[0])
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_works_as_desired_for_author(self):
        """Страницы доступны для автора."""
        for address, _ in (*self.guest_addresses, *self.auth_addresses):
            with self.subTest():
                response = self.authorized_client_author.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_url_works_as_desired_for_user(self):
        """Страница edit недоступна не автору."""
        response = self.authorized_client.get(self.EDIT[0])
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_not_existing_url_returns_404(self):
        """Несуществующая страница возвращает 404."""
        response = self.guest.get('/notexistingpage/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND,)
