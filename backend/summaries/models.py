from django.contrib.auth.models import User
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.utils.text import slugify


class Tag(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Summary(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)  # the book's author
    body = models.TextField()  # Markdown
    tags = models.ManyToManyField(Tag, related_name="summaries", blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="summaries"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    medium_url = models.URLField(null=True, blank=True)

    # Populated from title + body for PostgreSQL full-text search (see search.py).
    search_vector = SearchVectorField(null=True, blank=True, editable=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [GinIndex(fields=["search_vector"], name="summary_search_gin")]

    def __str__(self):
        return self.title
