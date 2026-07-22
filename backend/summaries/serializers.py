from django.utils.text import slugify
from rest_framework import serializers

from .models import Summary, Tag
from .search import update_search_vector


class TagSerializer(serializers.ModelSerializer):
    summary_count = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Tag
        fields = ["id", "name", "slug", "summary_count"]


class SummaryListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    created_by = serializers.CharField(source="created_by.username", read_only=True)
    created_by_id = serializers.IntegerField(source="created_by.id", read_only=True)

    class Meta:
        model = Summary
        fields = [
            "id",
            "title",
            "author",
            "tags",
            "created_by",
            "created_by_id",
            "created_at",
            "updated_at",
            "is_published",
            "medium_url",
        ]


class SummaryDetailSerializer(SummaryListSerializer):
    class Meta(SummaryListSerializer.Meta):
        fields = SummaryListSerializer.Meta.fields + ["body"]


class SummaryWriteSerializer(serializers.ModelSerializer):
    # Tags are supplied as a plain list of names; created on the fly.
    tags = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        write_only=True,
    )

    class Meta:
        model = Summary
        fields = ["id", "title", "author", "body", "tags", "is_published"]
        read_only_fields = ["id", "is_published"]  # publishing is a separate endpoint

    def _set_tags(self, summary, tag_names):
        tag_objs = []
        for raw in tag_names:
            name = raw.strip()
            if not name:
                continue
            tag, _ = Tag.objects.get_or_create(
                slug=slugify(name), defaults={"name": name}
            )
            tag_objs.append(tag)
        summary.tags.set(tag_objs)

    def create(self, validated_data):
        tag_names = validated_data.pop("tags", [])
        summary = Summary.objects.create(
            created_by=self.context["request"].user, **validated_data
        )
        self._set_tags(summary, tag_names)
        update_search_vector(summary)
        return summary

    def update(self, instance, validated_data):
        tag_names = validated_data.pop("tags", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        if tag_names is not None:
            self._set_tags(instance, tag_names)
        update_search_vector(instance)
        return instance
