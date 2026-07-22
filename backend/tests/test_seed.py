import pytest
from django.contrib.auth.models import User
from django.core.management import call_command

from summaries.models import Summary, Tag

pytestmark = pytest.mark.django_db


def test_seed_creates_data():
    call_command("seed")
    assert User.objects.filter(username="alice").exists()
    assert User.objects.filter(username="bob").exists()
    assert Tag.objects.count() >= 5
    assert Summary.objects.filter(is_published=True).count() >= 4
    # Seeded summaries are searchable (search vector populated).
    assert Summary.objects.filter(title="Atomic Habits").exists()


def test_seed_is_idempotent():
    call_command("seed")
    call_command("seed")  # exercises the "already exists" branches
    assert User.objects.filter(username="alice").count() == 1
    assert Summary.objects.filter(title="Atomic Habits").count() == 1
