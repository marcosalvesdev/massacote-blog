from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView,
)
from post.models import Post
from post.forms.post_form import PostForm


class PostListView(ListView):
    model = Post
    template_name = "post/list.html"
    context_object_name = "posts"
    paginate_by = 20

    def get_queryset(self):
        return Post.objects.all().order_by("-created_at").select_related("author")


class PostDetailView(DetailView):
    model = Post
    template_name = "post/detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return Post.objects.filter(slug=self.kwargs["slug"]).select_related("author")


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "post/create.html"
    context_object_name = "form"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "post/delete.html"
    context_object_name = "post"
    success_url = reverse_lazy("post:list")

    def get_queryset(self):
        return Post.objects.filter(slug=self.kwargs["slug"], author=self.request.user)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "post/update.html"
    context_object_name = "post"

    def get_queryset(self):
        return Post.objects.filter(slug=self.kwargs["slug"], author=self.request.user)
