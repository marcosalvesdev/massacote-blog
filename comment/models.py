from django.db import models


# Create your models here.
class Comment(models.Model):
    post = models.ForeignKey(
        "post.Post", on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, related_name="comments"
    )
    content = models.TextField(max_length=500)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"
