from django.urls import path

from pages.views import AboutView

app_name = "pages"

urlpatterns = [
    path("about/", AboutView.as_view(), name="about"),
]
