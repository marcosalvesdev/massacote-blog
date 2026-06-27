from django.contrib.auth.models import User
from django.test import TestCase

from comment.models import Comment
from post.models import Post


class CommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pass")
        self.post = Post.objects.create(
            title="A Post",
            slug="a-post",
            content="Some content.",
            author=self.user,
        )

    def test_str(self):
        comment = Comment(post=self.post, author=self.user, content="Nice post!")

        self.assertEqual(str(comment), "Comment by alice on A Post")

    def test_is_approved_defaults_to_false(self):
        comment = Comment.objects.create(
            post=self.post, author=self.user, content="Nice post!"
        )

        self.assertFalse(comment.is_approved)
