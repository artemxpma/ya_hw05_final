# This Python file uses the following encoding: utf-8
from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост более пятнадцати символов',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        bundle = zip([self.post, self.group],
                     [self.post.text[:15], 'Тестовая группа'])
        for model, text in bundle:
            with self.subTest():
                self.assertEqual(str(model)[:15], text)

    def test_post_model_verbose_help(self):
        '''Проверит, что у Post поля verbose и help_text заполнены корректно'''
        post = self.post
        fields = {
            post._meta.get_field('text').verbose_name: 'Текст поста',
            post._meta.get_field('text').help_text: 'Введите текст поста'
        }
        for field, text in fields.items():
            with self.subTest():
                self.assertEqual(field, text)
