from django import forms
from django.utils.text import slugify
from post.models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["cover_image", "title", "excerpt", "content"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "post-form__title-input"}),
        }

    def clean_title(self):
        title = self.cleaned_data["title"]
        slug = slugify(title)
        if Post.objects.filter(slug=slug).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(
                "Já existe um post com este título. Escolha um título diferente."
            )
        self.instance.slug = slug
        return title
