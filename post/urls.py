from django.urls import path

from post.views import (
    PostListView,
    PostDetailView,
    PostCreateView,
    PostDeleteView,
    PostUpdateView,
)

app_name = "post"
URL_PREFIX = "posts/"

urlpatterns = [
    path("", PostListView.as_view(), name="list"),
    path(f"{URL_PREFIX}create/", PostCreateView.as_view(), name="create"),
    path(f"{URL_PREFIX}<str:slug>/", PostDetailView.as_view(), name="detail"),
    path(f"{URL_PREFIX}<str:slug>/update/", PostUpdateView.as_view(), name="update"),
    path(f"{URL_PREFIX}<str:slug>/delete/", PostDeleteView.as_view(), name="delete"),
]
