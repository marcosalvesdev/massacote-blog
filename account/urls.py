from django.urls import path
from account.views.user import (
    DetailUserView,
    CreateUserView,
    DeleteUserView,
    UpdateUserView,
)

app_name = "account"
URL_PREFIX = "<str:username>/"

urlpatterns = [
    path("create/", CreateUserView.as_view(), name="create"),
    path(f"{URL_PREFIX}delete/", DeleteUserView.as_view(), name="delete"),
    path(f"{URL_PREFIX}update/", UpdateUserView.as_view(), name="update"),
    path(f"{URL_PREFIX}", DetailUserView.as_view(), name="detail"),
]
