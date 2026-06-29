from django.contrib.auth.models import User
from django.test import TestCase

from post.forms.post_form import PostForm
from post.models import Post


class PostFormTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="author", password="pw12345")

    def test_valid_data_derives_slug_from_title(self):
        form = PostForm(data={"title": "Hello World", "excerpt": "", "content": "hi"})

        is_valid = form.is_valid()

        self.assertTrue(is_valid)
        self.assertEqual(form.instance.slug, "hello-world")

    def test_duplicate_title_on_create_is_rejected(self):
        Post.objects.create(
            title="Hello World",
            slug="hello-world",
            author=self.author,
            content="existing",
        )

        form = PostForm(data={"title": "Hello World", "excerpt": "", "content": "new"})

        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_editing_post_with_its_own_unchanged_title_is_accepted(self):
        post = Post.objects.create(
            title="Hello World",
            slug="hello-world",
            author=self.author,
            content="original",
        )

        form = PostForm(
            data={"title": "Hello World", "excerpt": "", "content": "updated"},
            instance=post,
        )

        self.assertTrue(form.is_valid())

    def test_editing_post_to_match_another_posts_title_is_rejected(self):
        Post.objects.create(
            title="Taken Title",
            slug="taken-title",
            author=self.author,
            content="other post",
        )
        post_being_edited = Post.objects.create(
            title="Original Title",
            slug="original-title",
            author=self.author,
            content="mine",
        )

        form = PostForm(
            data={"title": "Taken Title", "excerpt": "", "content": "mine"},
            instance=post_being_edited,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_title_producing_empty_slug_is_rejected(self):
        form = PostForm(data={"title": "!!!", "excerpt": "", "content": "x"})

        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)
