from django.urls import path

from post.views import (
    PostListView,
    PostDetailView,
    PostCreateView,
    PostDeleteView,
    PostEditView,
)

app_name = "post"
URL_PREFIX = "posts/"

urlpatterns = [
    path("", PostListView.as_view(), name="list"),
    path(f"{URL_PREFIX}create/", PostCreateView.as_view(), name="create"),
    path(f"{URL_PREFIX}<str:slug>/", PostDetailView.as_view(), name="detail"),
    path(f"{URL_PREFIX}<str:slug>/edit/", PostEditView.as_view(), name="edit"),
    path(f"{URL_PREFIX}<str:slug>/delete/", PostDeleteView.as_view(), name="delete"),
]
