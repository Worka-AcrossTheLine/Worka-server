from rest_framework import serializers
import json
import six

from .models import Post, Comment, Link, LinkTag
from django.contrib.auth import get_user_model
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
        fields = ("pk", "username", "user_image")


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
    # liked_by_req_user = serializers.SerializerMethodField()
    tags = NewTagListSerializerField()
    # my_mento = serializers.SerializerMethodField("mento_field")
    #
    # def mento_field(self, card):
    #     if "request" in self.context:
    #         user = self.context["request"].user
    #         return card.author.follower.filter(pk=user.pk).exists()

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
            # "liked_by_req_user",
            "tags",
            # "my_mento",
        )

    def get_number_of_comments(self, obj):
        return Comment.objects.filter(post=obj).count()

    def get_post_comments(self, obj):
        return Comment.objects.filter(post=obj)

    # def get_liked_by_req_user(self, obj):
    #     user = self.context["request"].user
    #     return user in obj.likes.all()


class LinkSerializer(TaggitSerializer, serializers.ModelSerializer):
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
