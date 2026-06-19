from django.db import models
from django.utils.text import Truncator

READING_WORDS_PER_MINUTE = 200


def post_cover_path(instance, filename):
    return f"post_covers/{instance.author_id}/{filename}"


class Post(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    content = models.TextField()
    excerpt = models.CharField(max_length=300, blank=True)
    slug = models.SlugField(unique=True)
    cover_image = models.ImageField(upload_to=post_cover_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("post:detail", kwargs={"slug": self.slug})

    def get_excerpt(self):
        return self.excerpt or Truncator(self.content).words(30, truncate="...")

    @property
    def reading_time(self):
        word_count = len(self.content.split())
        return max(1, round(word_count / READING_WORDS_PER_MINUTE))
