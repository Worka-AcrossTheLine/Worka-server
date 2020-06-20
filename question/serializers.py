from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import Page, Comments, Question, Tag

User = get_user_model()


class AuthorSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "pk",
            "username",
            "user_image",
        ]


class PageSerializer(serializers.ModelSerializer):
    author = AuthorSerializers(read_only=True)
    tags = serializers.SlugRelatedField(
        many=True, slug_field="name", queryset=Tag.objects.all()
    )
    questions = serializers.SerializerMethodField("questions_count")

    def questions_count(self, question):
        return Question.objects.filter(page=question).count()

    class Meta:
        model = Page
        fields = [
            "id",
            "author",
            "title",
            "tags",
            "questions",
            "created_at",
        ]


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            "id",
            "content",
            "created_at",
        ]


class CommentsSerializer(serializers.ModelSerializer):
    author = AuthorSerializers(read_only=True)
    is_like = serializers.SerializerMethodField("is_like_field")
    is_unlike = serializers.SerializerMethodField("is_unlike_field")
    like_count = serializers.SerializerMethodField("like_count_field")
    unlike_count = serializers.SerializerMethodField("unlike_count_field")
    is_mento = serializers.SerializerMethodField("is_mento_field")

    def is_like_field(self, comment):
        if "request" in self.context:
            user = self.context["request"].user
            return comment.like_user_set.filter(pk=user.pk).exists()

    def is_unlike_field(self, comment):
        if "request" in self.context:
            user = self.context["request"].user
            return comment.unlike_user_set.filter(pk=user.pk).exists()

    def like_count_field(self, comment):
        return comment.like_user_set.count()

    def unlike_count_field(self, comment):
        return comment.unlike_user_set.count()

    def is_mento_field(self, obj):
        if "request" in self.context:
            user = self.context["request"].user
            user = User.objects.get(pk=user.pk)
            return user.is_mento

    class Meta:
        model = Comments
        fields = [
            "id",
            "author",
            "text",
            "is_like",
            "is_unlike",
            "like_count",
            "unlike_count",
            "is_mento",
            "created_at",
        ]
