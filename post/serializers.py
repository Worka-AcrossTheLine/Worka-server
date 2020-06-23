from rest_framework import serializers

from .models import Post, Link, LinkTag, PostTag
from django.contrib.auth import get_user_model


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            "pk",
            "username",
            "user_image",
        ]


class PostSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    images = serializers.ImageField(max_length=None, allow_empty_file=False)
    tags = serializers.SlugRelatedField(
        many=True, slug_field="name", queryset=PostTag.objects.all()
    )

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "title",
            "images",
            "text",
            "created_at",
            "tags",
        ]


class LinkSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    tag = serializers.SlugRelatedField(
        many=True, slug_field="name", queryset=LinkTag.objects.all()
    )
    is_author = serializers.SerializerMethodField("is_author_field")

    def is_author_field(self, obj):
        if "request" in self.context:
            user = self.context["request"].user
            return obj.author == user

    class Meta:
        model = Link
        fields = [
            "pk",
            "author",
            "title",
            "tag",
            "url",
            "is_author",
            "created_at",
        ]
