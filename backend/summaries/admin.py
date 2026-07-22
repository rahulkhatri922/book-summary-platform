from django.contrib import admin

from .models import Summary, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Summary)
class SummaryAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "created_by", "is_published", "created_at")
    list_filter = ("is_published", "tags")
    search_fields = ("title", "author", "body")
    filter_horizontal = ("tags",)
