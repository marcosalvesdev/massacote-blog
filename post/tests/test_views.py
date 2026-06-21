from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from post.models import Post


class PostListViewTests(TestCase):
    def test_list_page_returns_ok(self):
        response = self.client.get(reverse("post:list"))

        self.assertEqual(response.status_code, 200)

    def test_list_orders_posts_newest_first(self):
        author = User.objects.create_user(username="author", password="pw12345")
        older = Post.objects.create(
            title="Older", slug="older", author=author, content="x"
        )
        newer = Post.objects.create(
            title="Newer", slug="newer", author=author, content="x"
        )
        # auto_now_add ignores explicit values on save(), so back-date "older"
        # via update() to guarantee a deterministic, non-flaky ordering.
        Post.objects.filter(pk=older.pk).update(
            created_at=timezone.now() - timedelta(days=1)
        )

        response = self.client.get(reverse("post:list"))

        self.assertEqual(list(response.context["posts"]), [newer, older])


class PostDetailViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="author", password="pw12345")
        self.post = Post.objects.create(
            title="A Post", slug="a-post", author=self.author, content="body"
        )

    def test_existing_slug_returns_ok(self):
        response = self.client.get(reverse("post:detail", kwargs={"slug": "a-post"}))

        self.assertEqual(response.status_code, 200)

    def test_unknown_slug_returns_not_found(self):
        response = self.client.get(
            reverse("post:detail", kwargs={"slug": "does-not-exist"})
        )

        self.assertEqual(response.status_code, 404)


class PostCreateViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="author", password="pw12345")

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse("post:create"))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('post:create')}",
        )

    def test_authenticated_user_can_create_a_post(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("post:create"),
            {"title": "New Post", "excerpt": "", "content": "hello there"},
        )

        post = Post.objects.get(slug="new-post")
        self.assertRedirects(response, post.get_absolute_url())
        self.assertEqual(post.author, self.author)


class PostUpdateViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="author", password="pw12345")
        self.other_user = User.objects.create_user(username="other", password="pw12345")
        self.post = Post.objects.create(
            title="Original", slug="original", author=self.author, content="body"
        )

    def test_owner_can_update_their_post(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("post:update", kwargs={"slug": "original"}),
            {"title": "Original", "excerpt": "", "content": "updated body"},
        )

        self.post.refresh_from_db()
        self.assertRedirects(response, self.post.get_absolute_url())
        self.assertEqual(self.post.content, "updated body")

    def test_non_owner_cannot_update_someone_elses_post(self):
        self.client.force_login(self.other_user)

        response = self.client.get(
            reverse("post:update", kwargs={"slug": "original"})
        )

        self.assertEqual(response.status_code, 404)


class PostDeleteViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="author", password="pw12345")
        self.other_user = User.objects.create_user(username="other", password="pw12345")
        self.post = Post.objects.create(
            title="To Delete", slug="to-delete", author=self.author, content="body"
        )

    def test_owner_can_delete_their_post(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("post:delete", kwargs={"slug": "to-delete"})
        )

        self.assertRedirects(response, reverse("post:list"))
        self.assertFalse(Post.objects.filter(slug="to-delete").exists())

    def test_non_owner_cannot_delete_someone_elses_post(self):
        self.client.force_login(self.other_user)

        response = self.client.post(
            reverse("post:delete", kwargs={"slug": "to-delete"})
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Post.objects.filter(slug="to-delete").exists())
