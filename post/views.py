from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Case, Count, Prefetch, When
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView,
)

from comment.models import Comment
from post.models import Post, Status
from post.forms.post_form import PostForm
from comment.forms.comment_form import CommentForm


class PostListView(ListView):
    model = Post
    template_name = "post/list.html"
    context_object_name = "posts"
    paginate_by = 20

    def get_queryset(self):
        return (
            Post.objects.filter(status=Status.PUBLISHED, is_approved=True)
            .order_by("-created_at")
            .select_related("author")
        )


class PostDetailView(DetailView):
    model = Post
    template_name = "post/detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return (
            Post.objects.filter(
                slug=self.kwargs["slug"], status=Status.PUBLISHED, is_approved=True
            )
            .select_related("author")
            .prefetch_related(
                Prefetch(
                    "comments",
                    queryset=Comment.objects.filter(is_approved=True).select_related(
                        "author"
                    ),
                )
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comments"] = self.object.comments.all()
        context["comment_form"] = CommentForm()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "post/create.html"
    context_object_name = "form"
    success_url = reverse_lazy("post:mine")

    def form_valid(self, form):
        form.instance.author = self.request.user
        action = self.request.POST.get("action", Status.DRAFT)
        form.instance.status = Status.PENDING if action == "publish" else Status.DRAFT
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "post/delete.html"
    context_object_name = "post"
    success_url = reverse_lazy("post:mine")

    def get_queryset(self):
        return Post.objects.filter(slug=self.kwargs["slug"], author=self.request.user)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "post/update.html"
    context_object_name = "post"

    def get_queryset(self):
        return Post.objects.filter(slug=self.kwargs["slug"], author=self.request.user)

    def form_valid(self, form):
        action = self.request.POST.get("action", Status.DRAFT)
        form.instance.status = Status.PENDING if action == "publish" else Status.DRAFT
        return super().form_valid(form)

    def get_success_url(self):
        if self.object.status == Status.PUBLISHED:
            return self.object.get_absolute_url()
        return reverse("post:mine")


class UserPostsView(LoginRequiredMixin, View):
    paginate_by = 10

    def get(self, request):
        counts = Post.objects.filter(author=request.user).aggregate(
            draft_count=Count(Case(When(status=Status.DRAFT, then=1))),
            pending_count=Count(Case(When(status=Status.PENDING, then=1))),
            published_count=Count(
                Case(When(status=Status.PUBLISHED, is_approved=True, then=1))
            ),
        )
        qs = Post.objects.filter(author=request.user, status=Status.DRAFT).order_by(
            "-created_at"
        )
        page = Paginator(qs, self.paginate_by).get_page(request.GET.get("page", 1))
        return render(
            request,
            "post/user_posts.html",
            {"posts": page, "status": Status.DRAFT, **counts},
        )


class UserPostsByStatusView(LoginRequiredMixin, View):
    paginate_by = 5
    FILTERS = {
        Status.PUBLISHED: dict(status=Status.PUBLISHED, is_approved=True),
        Status.PENDING: dict(status=Status.PENDING),
        Status.DRAFT: dict(status=Status.DRAFT),
    }

    def get(self, request, status):
        filters = self.FILTERS.get(status, self.FILTERS[Status.DRAFT])
        qs = Post.objects.filter(author=request.user, **filters).order_by("-created_at")
        page = Paginator(qs, self.paginate_by).get_page(request.GET.get("page", 1))
        return render(
            request, "post/partials/_user_posts.html", {"posts": page, "status": status}
        )
