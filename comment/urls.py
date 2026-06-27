from django.urls import path

from comment.views import CommentCreateView


app_name = "comment"

urlpatterns = [
    path("<str:slug>/create/", CommentCreateView.as_view(), name="comment_create"),
]
