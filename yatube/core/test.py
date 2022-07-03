from django.contrib.auth import get_user_model
from django.test import TestCase, Client


User = get_user_model()


class PostsTests(TestCase):
    def setUp(self):
        self.guest = Client()

    def test_404_uses_custom_template(self):
        """404 использует кастомный шаблон."""
        response = self.guest.get('/notexistingpage/')
        self.assertTemplateUsed(response, 'core/404.html')
