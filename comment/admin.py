from django.contrib import admin

from comment.models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["post", "author", "created_at", "is_approved"]
    list_filter = ["is_approved"]
    list_editable = ["is_approved"]
    ordering = ["-created_at"]
