from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy

from account.forms.profile import ProfileForm
from account.forms.user import UserForm


User = get_user_model()


class DetailUserView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "account/user.html"
    context_object_name = "profile_user"

    def get_object(self, queryset=None):
        return self.request.user


class CreateUserView(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = "account/create.html"
    success_url = reverse_lazy("login")


class DeleteUserView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = "account/delete.html"
    success_url = reverse_lazy("post:list")

    def get_object(self, queryset=None):
        return self.request.user


class UpdateUserView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = "account/update.html"
    form_class = UserForm

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse("account:detail", kwargs={"username": self.object.username})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("profile_form", ProfileForm(instance=self.object.profile))
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        profile_form = ProfileForm(
            request.POST, request.FILES, instance=self.object.profile
        )
        if form.is_valid() and profile_form.is_valid():
            profile_form.save()
            return self.form_valid(form=form)
        else:
            return self.render_to_response(
                self.get_context_data(form=form, profile_form=profile_form)
            )
