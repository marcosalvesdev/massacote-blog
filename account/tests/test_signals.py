from django.contrib.auth.models import User
from django.test import TestCase

from account.models import Profile


class CreateUserProfileSignalTests(TestCase):
    def test_creating_a_user_auto_creates_a_profile(self):
        user = User.objects.create_user(username="marcos", password="pw12345")

        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_saving_an_existing_user_does_not_create_a_second_profile(self):
        user = User.objects.create_user(username="marcos", password="pw12345")

        user.email = "marcos@example.com"
        user.save()

        self.assertEqual(Profile.objects.filter(user=user).count(), 1)
