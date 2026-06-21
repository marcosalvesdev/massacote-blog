from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from account.models import Profile
from post.models import Post


class SignupLoginAndPostFlowTests(TestCase):
    """End-to-end walk through signup -> profile creation -> authoring a post."""

    def test_new_user_can_sign_up_log_in_and_publish_a_post(self):
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
            {"title": "My First Post", "excerpt": "", "content": "Hello, blog!"},
        )
        post = Post.objects.get(slug="my-first-post")
        self.assertRedirects(create_response, post.get_absolute_url())
        self.assertEqual(post.author, user)

        list_response = self.client.get(reverse("post:list"))
        self.assertContains(list_response, "My First Post")
