from django.contrib.auth.models import User
from django.test import TestCase

from account.forms.profile import ProfileForm
from account.forms.user import UserForm


class UserFormTests(TestCase):
    def test_valid_data_is_accepted(self):
        form = UserForm(
            data={
                "username": "marcos",
                "email": "marcos@example.com",
                "first_name": "Marcos",
                "last_name": "Alves",
            }
        )

        self.assertTrue(form.is_valid())

    def test_username_is_required(self):
        form = UserForm(data={"username": "", "email": "marcos@example.com"})

        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_does_not_expose_a_password_field(self):
        form = UserForm()

        self.assertNotIn("password", form.fields)


class ProfileFormTests(TestCase):
    def test_blank_bio_and_avatar_are_both_valid(self):
        form = ProfileForm(data={"bio": ""})

        self.assertTrue(form.is_valid())

    def test_bio_is_saved(self):
        user = User.objects.create_user(username="marcos", password="pw12345")
        form = ProfileForm(data={"bio": "Hello, I write about tech."}, instance=user.profile)

        form.save()

        user.profile.refresh_from_db()
        self.assertEqual(user.profile.bio, "Hello, I write about tech.")
