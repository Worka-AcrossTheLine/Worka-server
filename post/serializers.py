from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Post, PostTag

User = get_user_model()


class AuthorSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "pk",
            "username",
            "user_image",
        ]


class PostSerializer(serializers.ModelSerializer):
    author = AuthorSerializers(read_only=True)
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
