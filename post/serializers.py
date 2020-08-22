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
