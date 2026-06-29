from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from account.models import Profile
from post.models import Post, Status


class SignupLoginAndPostFlowTests(TestCase):
    """End-to-end walk through signup -> profile creation -> authoring a post."""

    def test_new_user_can_sign_up_log_in_and_submit_a_post_for_review(self):
        signup_response = self.client.post(
            reverse("account:create"),
            {
                "username": "marcos",
                "password1": "a-strong-pw-123",
                "password2": "a-strong-pw-123",
            },
        )
        self.assertRedirects(signup_response, reverse("login"))

        user = User.objects.get(username="marcos")
        self.assertTrue(Profile.objects.filter(user=user).exists())

        login_ok = self.client.login(username="marcos", password="a-strong-pw-123")
        self.assertTrue(login_ok)

        create_response = self.client.post(
            reverse("post:create"),
            {"title": "My First Post", "excerpt": "", "content": "Hello, blog!", "action": "publish"},
        )
        post = Post.objects.get(slug="my-first-post")
        self.assertRedirects(create_response, reverse("post:mine"))
        self.assertEqual(post.author, user)
        self.assertEqual(post.status, Status.PENDING)

        # PENDING posts require admin approval before appearing in the public feed
        list_response = self.client.get(reverse("post:list"))
        self.assertNotContains(list_response, "My First Post")
