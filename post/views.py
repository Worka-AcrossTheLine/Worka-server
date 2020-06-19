from django.contrib.auth import get_user_model
from rest_framework import permissions, viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter

from accounts.models import Mbti
from .serializers import (
    PostSerializer,
    CommentSerializer,
    AuthorSerializer,
    LinkSerializer,
)
from .models import Post, Comment, Link, LinkTag
from .permissions import IsOwnerOrReadOnly


# from django_filters.rest_framework import DjangoFilterBackend


class FeedViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().select_related("author").prefetch_related("likes")
    serializer_class = PostSerializer
    # permission_classes = (IsOwnerOrReadOnly, permissions.IsAuthenticatedOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        return super().perform_create(serializer)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        mbti = Mbti.objects.filter(title=self.request.user.mbti.title)
        user = get_user_model().objects.filter(mbti__in=mbti)
        qs = qs.filter(author__in=user)
        # user = self.request.user
        # following_users = user.following.all()  # user 모델 대입하세요
        # queryset = Post.objects.all().filter(author__in=following_users)
        return qs

    def get_object(self):
        pk = self.kwargs["pk"]
        post = Post.objects.get(pk=pk)
        return post

    @action(detail=True, methods=["POST"])
    def mento(self, *args, **kwargs):
        card = self.get_object()
        card_user = card.author
        current_user = self.request.user

        try:
            if current_user.following.filter(pk=card_user.pk).exists():
                card_user.follower.remove(current_user.pk)
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                card_user.follower.add(current_user.pk)
                return Response(status=status.HTTP_201_CREATED)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ProfileFeed(FeedViewSet):
    def get_queryset(self, *args, **kwargs):
        qs = Post.objects.filter(author_id=self.kwargs["account_pk"])
        return qs

    def perform_create(self, serializer):
        if self.kwargs["accounts_pk"] == str(self.request.user.pk):
            serializer.save(author=self.request.user)
            return super().perform_create(serializer)
        else:
            raise ValidationError("현재 프로필 유저만 작성할 수 있습니다.")


class CommentView(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = CommentSerializer
    # permission_classes = (
    #     IsOwnerOrReadOnly,
    #     permissions.IsAuthenticatedOrReadOnly,
    # )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        return super().perform_create(serializer)


class Like(APIView):
    queryset = Post.objects.all()

    def get(self, request, format=None, post_id=None):
        post = Post.objects.get(pk=post_id)
        user = self.request.user
        if user.is_authenticated:
            if user in post.likes.all():
                post.likes.remove(user)
                like = False
            else:
                post.likes.add(user)
                like = True

            data = {"like": like}

            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"err": "인증된 사용자만 접근가능"}, status=status.HTTP_401_UNAUTHORIZED
            )


class Likers(generics.ListAPIView):
    serializer_class = AuthorSerializer
    # permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        post_id = self.kwargs["post_id"]
        queryset = Post.objects.get(pk=post_id).likes.all()
        return queryset


class All(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    # permission_classes = (permissions.AllowAny,)
    filter_backends = [
        SearchFilter,
    ]
    search_fields = ["title", "author__username", "tags__name"]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class TagView(generics.ListAPIView):
    serializer_class = PostSerializer
    # permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        return Post.objects.filter(tags__slug=self.kwargs.get("slug"))

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class LinkModelViewSet(viewsets.ModelViewSet):
    """
            # 질문지(page) API
            ---
            # search GET
            # links/?search=example/
            ---
            # Allow Method GET, POST
            # /links/
            ---
            # Allow Method RETRIEVE(GET), PUT(사용X), PATCH, DELETE
            # /links/{id}/
            ---
            # request
            # POST, PATCH
                - title : STRING
                - tags : Array ex)[STRING, STRING ...]
                - url : url(STRING)
            ---
            # response
            # /links/
            # GET
                - "count": int,
                - "next": null,
                - "previous": null,
                - "results": [
                    {
                        "id": int,
                        "author": {
                            "pk": int,
                            "username": STRING,
                            "user_image": STRING
                        },
                        "title": STRING,
                        "tags": [STRING, STRING ...],
                        "is_author": Boolean or String(true, false),
                        "created_at": "2020-06-15T21:09:16.630261+09:00"
                    }
                ]

            # /links/{id}/
                - "id": int,
                - "author": {
                        -  "pk": int,
                         - "username": STRING,
                         - "user_image": STRING
                    },
                - "title": STRING,
                - "tags": [STRING, STRING ...],
                - "questions": Boolean or String(true, false),
                - "created_at": "2020-06-15T21:09:16.630261+09:00"
    """

    serializer_class = LinkSerializer
    queryset = Link.objects.all().select_related("author").prefetch_related("tag")
    filter_backends = [
        SearchFilter,
    ]
    search_fields = ["title", "author__username", "tag__name"]

    def create(self, request, *args, **kwargs):
        tag_names = request.data.get("tag", [])
        for tag_name in tag_names:
            LinkTag.objects.get_or_create(name=tag_name)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        tag_names = request.data.get("tag", [])
        for tag_name in tag_names:
            LinkTag.objects.get_or_create(name=tag_name)
        return super().update(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        mbti = Mbti.objects.filter(title=self.request.user.mbti.title)
        user = get_user_model().objects.filter(mbti__in=mbti)
        qs = qs.filter(author__in=user)
        return qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        return super().perform_create(serializer)

    def perform_update(self, serializer):
        link = self.get_object()

        if link.author == self.request.user:
            serializer.save()
            return super().perform_update(serializer)
        else:
            raise ValidationError("작성자만 수정할 수 있습니다.")

    def perform_destroy(self, instance):
        if instance.author == self.request.user:
            instance.delete()
        else:
            raise ValidationError("작성자가 아닙니다.")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context
