from django.test import TestCase

from comment.forms.comment_form import CommentForm


class CommentFormTest(TestCase):
    def test_valid_with_content(self):
        form = CommentForm(data={"content": "Great article!"})

        self.assertTrue(form.is_valid())

    def test_invalid_when_content_is_empty(self):
        form = CommentForm(data={"content": ""})

        self.assertFalse(form.is_valid())
        self.assertIn("content", form.errors)

    def test_invalid_when_content_exceeds_max_length(self):
        form = CommentForm(data={"content": "x" * 501})

        self.assertFalse(form.is_valid())
        self.assertIn("content", form.errors)
