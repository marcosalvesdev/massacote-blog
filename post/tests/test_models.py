from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from post.models import Post, Status, post_cover_path


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


class PostCleanTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="author", password="pw12345")

    def _post(self, status, is_approved):
        return Post(
            title="T", slug="t", author=self.author, content="x",
            status=status, is_approved=is_approved,
        )

    def test_published_without_approval_raises(self):
        post = self._post(Status.PUBLISHED, is_approved=False)

        with self.assertRaises(ValidationError):
            post.clean()

    def test_published_and_approved_does_not_raise(self):
        post = self._post(Status.PUBLISHED, is_approved=True)

        post.clean()

    def test_draft_without_approval_does_not_raise(self):
        post = self._post(Status.DRAFT, is_approved=False)

        post.clean()

    def test_pending_without_approval_does_not_raise(self):
        post = self._post(Status.PENDING, is_approved=False)

        post.clean()


class PostCoverPathTests(TestCase):
    def test_path_is_keyed_by_author_username(self):
        author = User.objects.create_user(username="author", password="pw12345")
        post = Post(title="Title", author=author, content="hello")

        path = post_cover_path(post, "cover.png")

        self.assertEqual(path, "author/post_covers/cover.png")
