import itertools

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from faker import Faker

from comment.models import Comment
from post.models import Post

User = get_user_model()
fake = Faker()

COMMENTS_PER_POST = 3


class Command(BaseCommand):
    help = "Seed the database with fake comments for existing posts."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear-only",
            action="store_true",
            help="Delete all existing comments without seeding new data.",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing comments before seeding.",
        )
        parser.add_argument(
            "--comments",
            type=int,
            default=COMMENTS_PER_POST,
            help=f"Number of comments per post (default: {COMMENTS_PER_POST}).",
        )

    def handle(self, *args, **options):
        if options["clear"] or options["clear_only"]:
            Comment.objects.all().delete()
            self.stdout.write("Removed all existing comments.")

        if options["clear_only"]:
            return

        posts = list(Post.objects.all())
        users = list(User.objects.filter(is_superuser=False))

        if not posts:
            self.stdout.write(self.style.WARNING("No posts found. Run seed_posts first."))
            return
        if not users:
            self.stdout.write(self.style.WARNING("No users found. Run seed_posts first."))
            return

        comments_per_post = options["comments"]
        self.stdout.write(f"Seeding {comments_per_post} comments per post ({len(posts)} posts)...")

        user_cycle = itertools.cycle(users)
        total = 0
        for post in posts:
            for _ in range(comments_per_post):
                Comment.objects.create(
                    post=post,
                    author=next(user_cycle),
                    content=fake.paragraph(nb_sentences=3),
                    is_approved=True,
                )
                total += 1

        self.stdout.write(self.style.SUCCESS(f"Done. {total} comments created."))
