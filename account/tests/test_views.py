from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class CreateUserViewTests(TestCase):
    def test_signup_page_returns_ok(self):
        response = self.client.get(reverse("account:create"))

        self.assertEqual(response.status_code, 200)

    def test_valid_signup_creates_a_user_and_redirects_to_login(self):
        response = self.client.post(
            reverse("account:create"),
            {
                "username": "marcos",
                "password1": "a-strong-pw-123",
                "password2": "a-strong-pw-123",
            },
        )

        self.assertRedirects(response, reverse("login"))
        self.assertTrue(User.objects.filter(username="marcos").exists())


class DetailUserViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="marcos", password="pw12345")

    def test_anonymous_user_is_redirected_to_login(self):
        url = reverse("account:detail", kwargs={"username": "marcos"})

        response = self.client.get(url)

        self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_logged_in_user_sees_their_profile(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("account:detail", kwargs={"username": "marcos"})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["profile_user"], self.user)


class UpdateUserViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="marcos",
            password="pw12345",
            first_name="Marcos",
            last_name="Alves",
            email="old@example.com",
        )

    def test_updates_both_user_and_profile_fields_together(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("account:update", kwargs={"username": "marcos"}),
            {
                "username": "marcos",
                "first_name": "Marcos",
                "last_name": "Alves",
                "email": "new@example.com",
                "bio": "Hello, I write about tech.",
            },
        )

        self.user.refresh_from_db()
        self.assertRedirects(
            response, reverse("account:detail", kwargs={"username": "marcos"})
        )
        self.assertEqual(self.user.email, "new@example.com")
        self.assertEqual(self.user.profile.bio, "Hello, I write about tech.")

    def test_does_not_blank_out_first_and_last_name_on_unrelated_update(self):
        self.client.force_login(self.user)

        self.client.post(
            reverse("account:update", kwargs={"username": "marcos"}),
            {
                "username": "marcos",
                "first_name": "Marcos",
                "last_name": "Alves",
                "email": "old@example.com",
                "bio": "Just updating my bio.",
            },
        )

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Marcos")
        self.assertEqual(self.user.last_name, "Alves")

    def test_invalid_submission_rerenders_both_forms_with_errors(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("account:update", kwargs={"username": "marcos"}),
            {
                "username": "",
                "first_name": "Marcos",
                "last_name": "Alves",
                "email": "old@example.com",
                "bio": "Hello",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("username", response.context["form"].errors)


class DeleteUserViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="marcos", password="pw12345")

    def test_owner_can_delete_their_account(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("account:delete", kwargs={"username": "marcos"})
        )

        self.assertRedirects(response, reverse("post:list"))
        self.assertFalse(User.objects.filter(username="marcos").exists())
