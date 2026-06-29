from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from post.models import Post, Status


def make_post(author, title, slug, status=Status.DRAFT, is_approved=False, **kwargs):
    return Post.objects.create(
        title=title, slug=slug, author=author, content="x",
        status=status, is_approved=is_approved, **kwargs,
    )


class PostListViewTests(TestCase):
    def test_list_page_returns_ok(self):
        response = self.client.get(reverse("post:list"))

        self.assertEqual(response.status_code, 200)

    def test_list_orders_posts_newest_first(self):
        author = User.objects.create_user(username="author", password="pw12345")
        older = make_post(author, "Older", "older", status=Status.PUBLISHED, is_approved=True)
        newer = make_post(author, "Newer", "newer", status=Status.PUBLISHED, is_approved=True)
        Post.objects.filter(pk=older.pk).update(
            created_at=timezone.now() - timedelta(days=1)
        )

        response = self.client.get(reverse("post:list"))

        self.assertEqual(list(response.context["posts"]), [newer, older])

    def test_draft_and_unapproved_posts_are_excluded_from_list(self):
        author = User.objects.create_user(username="author", password="pw12345")
        make_post(author, "Draft", "draft", status=Status.DRAFT)
        make_post(author, "Pending", "pending", status=Status.PENDING)
        make_post(author, "Unapproved", "unapproved", status=Status.PUBLISHED, is_approved=False)

        response = self.client.get(reverse("post:list"))

        self.assertEqual(list(response.context["posts"]), [])


class PostDetailViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="author", password="pw12345")
        self.post = make_post(
            self.author, "A Post", "a-post",
            status=Status.PUBLISHED, is_approved=True,
        )

    def test_existing_slug_returns_ok(self):
        response = self.client.get(reverse("post:detail", kwargs={"slug": "a-post"}))

        self.assertEqual(response.status_code, 200)

    def test_unknown_slug_returns_not_found(self):
        response = self.client.get(
            reverse("post:detail", kwargs={"slug": "does-not-exist"})
        )

        self.assertEqual(response.status_code, 404)

    def test_draft_post_returns_not_found(self):
        draft = make_post(self.author, "Hidden", "hidden", status=Status.DRAFT)

        response = self.client.get(reverse("post:detail", kwargs={"slug": draft.slug}))

        self.assertEqual(response.status_code, 404)


class PostCreateViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="author", password="pw12345")

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse("post:create"))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('post:create')}",
        )

    def test_save_draft_action_creates_post_with_draft_status(self):
        self.client.force_login(self.author)

        self.client.post(
            reverse("post:create"),
            {"title": "New Post", "excerpt": "", "content": "hello", "action": "draft"},
        )

        post = Post.objects.get(slug="new-post")
        self.assertEqual(post.status, Status.DRAFT)
        self.assertEqual(post.author, self.author)

    def test_save_draft_redirects_to_mine(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("post:create"),
            {"title": "New Post", "excerpt": "", "content": "hello", "action": "draft"},
        )

        self.assertRedirects(response, reverse("post:mine"))

    def test_publish_action_creates_post_with_pending_status(self):
        self.client.force_login(self.author)

        self.client.post(
            reverse("post:create"),
            {"title": "Review Post", "excerpt": "", "content": "hello", "action": "publish"},
        )

        post = Post.objects.get(slug="review-post")
        self.assertEqual(post.status, Status.PENDING)


class PostUpdateViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="author", password="pw12345")
        self.other_user = User.objects.create_user(username="other", password="pw12345")
        self.post = make_post(self.author, "Original", "original")

    def test_owner_can_update_their_post(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("post:update", kwargs={"slug": "original"}),
            {"title": "Original", "excerpt": "", "content": "updated body", "action": "draft"},
        )

        self.post.refresh_from_db()
        self.assertRedirects(response, reverse("post:mine"))
        self.assertEqual(self.post.content, "updated body")

    def test_publish_action_sets_status_to_pending(self):
        self.client.force_login(self.author)

        self.client.post(
            reverse("post:update", kwargs={"slug": "original"}),
            {"title": "Original", "excerpt": "", "content": "body", "action": "publish"},
        )

        self.post.refresh_from_db()
        self.assertEqual(self.post.status, Status.PENDING)

    def test_non_owner_cannot_update_someone_elses_post(self):
        self.client.force_login(self.other_user)

        response = self.client.get(
            reverse("post:update", kwargs={"slug": "original"})
        )

        self.assertEqual(response.status_code, 404)


class PostDeleteViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="author", password="pw12345")
        self.other_user = User.objects.create_user(username="other", password="pw12345")
        self.post = make_post(self.author, "To Delete", "to-delete")

    def test_owner_can_delete_their_post(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("post:delete", kwargs={"slug": "to-delete"})
        )

        self.assertRedirects(response, reverse("post:mine"))
        self.assertFalse(Post.objects.filter(slug="to-delete").exists())

    def test_non_owner_cannot_delete_someone_elses_post(self):
        self.client.force_login(self.other_user)

        response = self.client.post(
            reverse("post:delete", kwargs={"slug": "to-delete"})
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Post.objects.filter(slug="to-delete").exists())


class UserPostsViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="author", password="pw12345")
        self.url = reverse("post:mine")

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(self.url)

        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_authenticated_user_gets_ok(self):
        self.client.force_login(self.author)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_counts_reflect_post_statuses(self):
        make_post(self.author, "D", "d", status=Status.DRAFT)
        make_post(self.author, "Pe", "pe", status=Status.PENDING)
        make_post(self.author, "Pu", "pu", status=Status.PUBLISHED, is_approved=True)
        self.client.force_login(self.author)

        response = self.client.get(self.url)

        self.assertEqual(response.context["draft_count"], 1)
        self.assertEqual(response.context["pending_count"], 1)
        self.assertEqual(response.context["published_count"], 1)

    def test_counts_exclude_other_authors_posts(self):
        other = User.objects.create_user(username="other", password="pw12345")
        make_post(other, "Other draft", "other-draft", status=Status.DRAFT)
        self.client.force_login(self.author)

        response = self.client.get(self.url)

        self.assertEqual(response.context["draft_count"], 0)


class UserPostsByStatusViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="author", password="pw12345")

    def test_anonymous_user_is_redirected_to_login(self):
        url = reverse("post:mine_by_status", kwargs={"status": "draft"})

        response = self.client.get(url)

        self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_draft_status_returns_only_drafts(self):
        make_post(self.author, "Draft", "draft", status=Status.DRAFT)
        make_post(self.author, "Pending", "pending", status=Status.PENDING)
        self.client.force_login(self.author)

        response = self.client.get(
            reverse("post:mine_by_status", kwargs={"status": "draft"})
        )

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context["posts"], ["draft"], transform=lambda p: p.slug)

    def test_pending_status_returns_only_pending(self):
        make_post(self.author, "Draft", "draft", status=Status.DRAFT)
        make_post(self.author, "Pending", "pending", status=Status.PENDING)
        self.client.force_login(self.author)

        response = self.client.get(
            reverse("post:mine_by_status", kwargs={"status": "pending"})
        )

        self.assertQuerySetEqual(response.context["posts"], ["pending"], transform=lambda p: p.slug)

    def test_published_status_excludes_unapproved(self):
        make_post(self.author, "Published", "published", status=Status.PUBLISHED, is_approved=True)
        make_post(self.author, "Unapproved", "unapproved", status=Status.PUBLISHED, is_approved=False)
        self.client.force_login(self.author)

        response = self.client.get(
            reverse("post:mine_by_status", kwargs={"status": "published"})
        )

        self.assertQuerySetEqual(response.context["posts"], ["published"], transform=lambda p: p.slug)

    def test_posts_from_other_authors_are_excluded(self):
        other = User.objects.create_user(username="other", password="pw12345")
        make_post(other, "Other", "other", status=Status.DRAFT)
        self.client.force_login(self.author)

        response = self.client.get(
            reverse("post:mine_by_status", kwargs={"status": "draft"})
        )

        self.assertQuerySetEqual(response.context["posts"], [])
