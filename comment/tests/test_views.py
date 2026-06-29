from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from comment.models import Comment
from post.models import Post, Status


class CommentCreateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="alice", password="pass")
        self.post = Post.objects.create(
            title="A Post",
            slug="a-post",
            content="Some content.",
            author=self.user,
            status=Status.PUBLISHED,
            is_approved=True,
        )
        self.url = reverse("comment:comment_create", kwargs={"slug": self.post.slug})

    def test_unauthenticated_user_is_redirected_to_login(self):
        response = self.client.post(self.url, {"content": "Hello!"})

        self.assertRedirects(response, f"/accounts/login/?next={self.url}")

    def test_authenticated_user_creates_comment(self):
        self.client.force_login(self.user)

        self.client.post(self.url, {"content": "Great post!"})

        self.assertTrue(Comment.objects.filter(post=self.post, author=self.user).exists())

    def test_comment_is_created_with_is_approved_false(self):
        self.client.force_login(self.user)

        self.client.post(self.url, {"content": "Great post!"})

        comment = Comment.objects.get(post=self.post)
        self.assertFalse(comment.is_approved)

    def test_success_redirects_to_post_detail(self):
        self.client.force_login(self.user)

        response = self.client.post(self.url, {"content": "Great post!"})

        self.assertRedirects(
            response, reverse("post:detail", kwargs={"slug": self.post.slug})
        )

    def test_invalid_slug_returns_404(self):
        self.client.force_login(self.user)
        url = reverse("comment:comment_create", kwargs={"slug": "does-not-exist"})

        response = self.client.post(url, {"content": "Hello!"})

        self.assertEqual(response.status_code, 404)

    def test_empty_content_does_not_create_comment(self):
        self.client.force_login(self.user)

        self.client.post(self.url, {"content": ""})

        self.assertFalse(Comment.objects.filter(post=self.post).exists())
