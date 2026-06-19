from django.contrib import admin
from post.models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "cover_image", "created_at", "updated_at")
    prepopulated_fields = {"slug": ("title",)}
