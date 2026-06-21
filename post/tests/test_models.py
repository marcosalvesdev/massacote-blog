from django.contrib.auth.models import User
from django.test import TestCase

from post.models import Post


class PostModelTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="author", password="pw12345")

    def test_str_returns_title(self):
        post = Post(title="My First Post", author=self.author, content="hello")

        result = str(post)

        self.assertEqual(result, "My First Post")

    def test_get_absolute_url_uses_slug(self):
        post = Post.objects.create(
            title="My First Post",
            slug="my-first-post",
            author=self.author,
            content="hello",
        )

        url = post.get_absolute_url()

        self.assertEqual(url, "/posts/my-first-post/")

    def test_get_excerpt_returns_explicit_excerpt_when_set(self):
        post = Post(
            title="Title",
            author=self.author,
            content="word " * 50,
            excerpt="A short manual excerpt.",
        )

        excerpt = post.get_excerpt()

        self.assertEqual(excerpt, "A short manual excerpt.")

    def test_get_excerpt_falls_back_to_truncated_content(self):
        post = Post(title="Title", author=self.author, content="word " * 50)

        excerpt = post.get_excerpt()

        self.assertEqual(excerpt, " ".join(["word"] * 30) + "...")

    def test_reading_time_rounds_to_nearest_minute(self):
        post = Post(title="Title", author=self.author, content="word " * 400)

        reading_time = post.reading_time

        self.assertEqual(reading_time, 2)

    def test_reading_time_is_never_less_than_one_minute(self):
        post = Post(title="Title", author=self.author, content="just a few words")

        reading_time = post.reading_time

        self.assertEqual(reading_time, 1)
