"""Seed the database with sample users, tags and summaries.

Usage: python manage.py seed
Idempotent — safe to run more than once.
"""
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from summaries.models import Summary, Tag
from summaries.search import update_search_vector

USERS = [
    {"username": "alice", "email": "alice@example.com", "password": "password123"},
    {"username": "bob", "email": "bob@example.com", "password": "password123"},
]

TAGS = ["productivity", "history", "psychology", "startups", "philosophy"]

SUMMARIES = [
    {
        "title": "Atomic Habits",
        "author": "James Clear",
        "owner": "alice",
        "tags": ["productivity", "psychology"],
        "body": (
            "# Atomic Habits\n\n"
            "Small, consistent improvements compound into remarkable results. "
            "Focus on **systems** rather than goals, and build *identity-based* "
            "habits: every action is a vote for the person you want to become.\n\n"
            "The habit loop is cue, craving, response, reward."
        ),
    },
    {
        "title": "Sapiens",
        "author": "Yuval Noah Harari",
        "owner": "alice",
        "tags": ["history"],
        "body": (
            "# Sapiens\n\n"
            "Humankind's rise is driven by shared fictions — money, nations, and "
            "religions — that let large numbers of strangers cooperate. Three "
            "revolutions shape the story: Cognitive, Agricultural, and Scientific."
        ),
    },
    {
        "title": "The Lean Startup",
        "author": "Eric Ries",
        "owner": "bob",
        "tags": ["startups", "productivity"],
        "body": (
            "# The Lean Startup\n\n"
            "Build-Measure-Learn as fast as possible. Ship a **Minimum Viable "
            "Product**, measure real customer behaviour, and either persevere or "
            "pivot based on validated learning."
        ),
    },
    {
        "title": "Meditations",
        "author": "Marcus Aurelius",
        "owner": "bob",
        "tags": ["philosophy"],
        "body": (
            "# Meditations\n\n"
            "A Stoic notebook. Focus only on what you control; your judgments, not "
            "external events, disturb you. Memento mori — time is short, so act with "
            "reason and virtue."
        ),
    },
]


class Command(BaseCommand):
    help = "Create sample users, tags and summaries."

    @transaction.atomic
    def handle(self, *args, **options):
        users = {}
        for spec in USERS:
            user, created = User.objects.get_or_create(
                username=spec["username"], defaults={"email": spec["email"]}
            )
            if created:
                user.set_password(spec["password"])
                user.save()
            users[spec["username"]] = user
            self.stdout.write(
                f"{'created' if created else 'exists '} user: {user.username}"
            )

        tags = {}
        for name in TAGS:
            tag, _ = Tag.objects.get_or_create(name=name)
            tags[name] = tag
        self.stdout.write(f"tags ready: {', '.join(tags)}")

        for spec in SUMMARIES:
            summary, created = Summary.objects.get_or_create(
                title=spec["title"],
                created_by=users[spec["owner"]],
                defaults={
                    "author": spec["author"],
                    "body": spec["body"],
                    "is_published": True,
                },
            )
            if created:
                summary.tags.set([tags[t] for t in spec["tags"]])
                update_search_vector(summary)
            self.stdout.write(
                f"{'created' if created else 'exists '} summary: {summary.title}"
            )

        self.stdout.write(self.style.SUCCESS("Seed complete."))
