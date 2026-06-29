from django.contrib import admin
from post.models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "status", "is_approved", "created_at")
    list_filter = ("status", "is_approved")
    list_editable = ("is_approved",)
    ordering = ("-created_at",)
    prepopulated_fields = {"slug": ("title",)}
