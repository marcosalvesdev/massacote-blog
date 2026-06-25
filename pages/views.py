from django.conf import settings
from django.views.generic import TemplateView


class AboutView(TemplateView):
    template_name = "pages/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["about_photo_url"] = settings.ABOUT_PHOTO_URL
        return context
