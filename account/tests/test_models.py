from django.contrib.auth.models import User
from django.test import TestCase

from account.models import Profile, get_avatar_path


class ProfileModelTests(TestCase):
    def test_str_includes_username(self):
        user = User.objects.create_user(username="marcos", password="pw12345")
        profile = user.profile

        result = str(profile)

        self.assertEqual(result, "Profile of marcos")


class GetAvatarPathTests(TestCase):
    def test_path_is_keyed_by_username(self):
        user = User.objects.create_user(username="marcos", password="pw12345")
        profile = Profile(user=user)

        path = get_avatar_path(profile, "photo.png")

        self.assertEqual(path, "marcos/profile_pictures/photo.png")
