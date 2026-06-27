from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404

from comment.models import Comment
from post.models import Post
from comment.forms.comment_form import CommentForm


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = "comment/comment_form.html"

    def get_success_url(self):
        return reverse_lazy("post:detail", kwargs={"slug": self.kwargs["slug"]})

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, slug=self.kwargs["slug"])
        return super().form_valid(form)
