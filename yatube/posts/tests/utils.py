from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Follow


def post_body_test(self, bundle):
    for first, second in bundle:
        with self.subTest():
            self.assertEqual(first, second)


def view_bundle(self, first_obj,
                additional_context=None,
                additional_value=None):
    '''
    Принимает данные setUp, первый объект контекста формы,
    и необязательную пару для проверки контекст-значение, и
    компанует кортежи для проверки.
    '''
    return ((first_obj.text, self.post.text),
            (first_obj.author.username, self.user.username),
            (first_obj.group.title, self.group.title),
            (first_obj.image, self.post.image),
            (additional_context, additional_value))


def reverse_ad(address, argument=None):
    return reverse(address, args=argument)


small_gif = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
uploaded_img = SimpleUploadedFile(
    name='small.gif',
    content=small_gif,
    content_type='image/gif'
)


def get_follow_model(self):
    return Follow.objects.filter(user=self.user_follower,
                                 author=self.user_author)
