from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify

from faker import Faker

from post.models import Post, Status

User = get_user_model()
fake = Faker()


USERS = 5
POSTS_PER_USER = 10


class Command(BaseCommand):
    help = "Seed the database with fake users and posts."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear-only",
            action="store_true",
            help="Remove all existing posts and non-superuser users without seeding new data.",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Remove all existing posts and non-superuser users before seeding.",
        )
        parser.add_argument(
            "--users",
            type=int,
            default=USERS,
            help=f"Number of users to create (default: {USERS}).",
        )
        parser.add_argument(
            "--posts",
            type=int,
            default=POSTS_PER_USER,
            help=f"Number of posts per user to create (default: {POSTS_PER_USER}).",
        )

    def handle(self, *args, **options):
        if options["clear"] or options["clear_only"]:
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write("Removed all non-superuser users and their posts.")

        if options["clear_only"]:
            return

        _users, _posts_per_user = (
            options.get("users"),
            options.get("posts"),
        )
        self.stdout.write(
            f"Seeding {_users} users and {_posts_per_user} posts per user..."
        )

        users = self._create_fake_users(_users)
        self._create_fake_posts(users, _posts_per_user)
        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Seeded {_users} users and {_users * _posts_per_user} posts."
            )
        )

    def _create_fake_users(self, num_users: int) -> list:
        users = []
        for _ in range(num_users):
            username = fake.user_name() + str(fake.random_int(min=1, max=1000))
            user = User.objects.create_user(
                username=username,
                email=fake.email(),
                password="pass1234",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
            )
            user.profile.bio = fake.text(max_nb_chars=200)
            user.profile.save()
            users.append(user)
            self.stdout.write(f"Created user: {username}")

        return users

    def _create_fake_posts(self, users: list, posts_per_user: int):
        for user in users:
            for _ in range(posts_per_user):
                title = fake.sentence(nb_words=6).rstrip(".")
                slug = self._unique_slug(title)
                Post.objects.create(
                    title=title,
                    author=user,
                    content="\n\n".join(fake.paragraphs(nb=5)),
                    excerpt=fake.sentence(nb_words=20),
                    slug=slug,
                    status=Status.PUBLISHED,
                )

    def _unique_slug(self, title: str) -> str:
        slug = slugify(title)
        if not Post.objects.filter(slug=slug).exists():
            return slug

        for i in range(1, 100):
            candidate = f"{slug}-{i}"
            if not Post.objects.filter(slug=candidate).exists():
                return candidate

        raise RuntimeError(f"Unable to generate a unique slug for: {title}")
