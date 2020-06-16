from rest_framework import serializers
import json
import six
from .models import Post, Comment
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from taggit_serializer.serializers import TagListSerializerField, TaggitSerializer


class NewTagListSerializerField(TagListSerializerField):
    def to_internal_value(self, value):
        if isinstance(value, six.string_types):
            if not value:
                value = "[]"
            try:
                if type(value) == str:
                    if value.__contains__('"') == True:
                        value = json.loads(value)
                    else:
                        value = value.split(",")

            except ValueError:
                self.fail("invalid_json")

        if not isinstance(value, list):
            self.fail("not_a_list", input_type=type(value).__name__)

        for s in value:
            if not isinstance(s, six.string_types):
                self.fail("not_a_str")

            self.child.run_validation(s)

        return value


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("username", "user_image")


class CommentSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "author", "text", "created_at", "updated_at")
        read_only_fields = ("author", "id", "created_at", "updated_at")


class PostSerializer(TaggitSerializer, serializers.ModelSerializer):

    author = AuthorSerializer(read_only=True)
    images = serializers.ImageField(max_length=None, allow_empty_file=False)
    number_of_comments = serializers.SerializerMethodField()
    post_comments = serializers.SerializerMethodField()
    liked_by_req_user = serializers.SerializerMethodField()
    tags = NewTagListSerializerField()

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "title",
            "images",
            "text",
            "created_at",
            "updated_at",
            "number_of_likes",
            "number_of_comments",
            "post_comments",
            "liked_by_req_user",
            "tags",
        )

    def get_number_of_comments(self, obj):
        return Comment.objects.filter(post=obj).count()

    def get_post_comments(self, obj):
        return Comment.objects.filter(post=obj)

    def get_liked_by_req_user(self, obj):
        user = self.context["request"].user
        return user in obj.likes.all()
