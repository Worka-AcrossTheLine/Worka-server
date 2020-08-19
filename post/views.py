from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter

from cutompagination import MyPagination

from .serializers import (
    PostSerializer,
    LinkSerializer,
)
from .models import Post, Link, LinkTag, PostTag


class FeedViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().select_related("author").prefetch_related("likes")
    serializer_class = PostSerializer
    pagination_class = MyPagination
    filter_backends = [
        SearchFilter,
    ]
    search_fields = ["title", "author__username", "tags__name"]

    def create(self, request, *args, **kwargs):
        tag_names = request.data.get("tags", [])
        for tag_name in tag_names:
            PostTag.objects.get_or_create(name=tag_name)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        tag_names = request.data.get("tags", [])
        for tag_name in tag_names:
            PostTag.objects.get_or_create(name=tag_name)
        return super().update(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        return super().perform_create(serializer)

    def perform_update(self, serializer):
        card = self.get_object()
        if card.author == self.request.user:
            serializer.save()
            return super().perform_update(serializer)

    def perform_destroy(self, instance):
        if instance.author == self.request.user:
            instance.delete()
        else:
            raise ValidationError("카드 작성자만 질문을 삭제할 수 있습니다.")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        # 추후 업데이트 예정
        # if self.request.user.mbti is not None:
        #     mbti = Mbti.objects.filter(title=self.request.user.mbti.title)
        #     user = get_user_model().objects.filter(mbti__in=mbti)
        #     qs = qs.filter(author__in=user)
        return qs

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
        # 추후 업데이트 예정
        # if self.request.user.mbti is None:
        #     mbti = Mbti.objects.filter(title=self.request.user.mbti.title)
        #     user = get_user_model().objects.filter(mbti__in=mbti)
        #     qs = qs.filter(author__in=user)
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
            raise ValidationError("작성자만 삭제할 수 있습니다.")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context
