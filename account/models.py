from django.db import models


def get_avatar_path(instance, filename):
    return f"{instance.user.username}/profile_pictures/{filename}"


class Profile(models.Model):
    avatar = models.ImageField(upload_to=get_avatar_path, blank=True, null=True)
    user = models.OneToOneField(
        "auth.User", on_delete=models.CASCADE, related_name="profile"
    )
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
