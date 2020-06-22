from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from cutompagination import MyPagination

from accounts.models import Mbti

from .models import Page, Question, Comments, Tag
from .serializers import (
    PageSerializer,
    CommentsSerializer,
    QuestionSerializer,
)


class PageViewSet(viewsets.ModelViewSet):
    """
            # 질문지(page) API
            ---
            # Allow Method GET, POST
            # /pages/
            ---
            # Allow Method RETRIEVE(GET), PUT(사용X), PATCH, DELETE
            # /pages/{id}/
            ---
            # request
            # POST, PATCH
                - title : STRING
                - tags : Array ex)[STRING, STRING ...]
            ---
            # response
            # /pages/
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
                        "questions": int,
                        "created_at": "2020-06-15T21:09:16.630261+09:00"
                    }
                ]

            # /pages/{id}/
                - "id": int,
                - "author": {
                        -  "pk": int,
                         - "username": STRING,
                         - "user_image": STRING
                    },
                - "title": STRING,
                - "tags": [STRING, STRING ...],
                - "questions": int,
                - "created_at": "2020-06-15T21:09:16.630261+09:00"
    """

    queryset = Page.objects.all().select_related("author").prefetch_related("tags")
    serializer_class = PageSerializer
    filter_backends = [
        SearchFilter,
    ]
    search_fields = ["title", "author__username", "tags__name"]
    pagination_class = MyPagination

    def create(self, request, *args, **kwargs):
        tag_names = request.data.get("tags", [])
        for tag_name in tag_names:
            Tag.objects.get_or_create(name=tag_name)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        tag_names = request.data.get("tags", [])
        for tag_name in tag_names:
            Tag.objects.get_or_create(name=tag_name)
        return super().update(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        # if self.request.user.mbti is not None:
        #     mbti = Mbti.objects.filter(title=self.request.user.mbti.title)
        #     user = get_user_model().objects.filter(mbti__in=mbti)
        #     qs = qs.filter(author__in=user)
        return qs

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    # TODO 질문지 3개 이상 작성 시 과금
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        return super().perform_create(serializer)

    def perform_update(self, serializer):
        page = self.get_object()
        if page.author == self.request.user:
            serializer.save()
            return super().perform_update(serializer)
        else:
            raise ValidationError("질문지 작성자만 질문을 수정할 수 있습니다.")

    def perform_destroy(self, instance):
        if instance.author == self.request.user:
            instance.delete()
        else:
            raise ValidationError("질문지 작성자만 질문을 삭제할 수 있습니다.")


class ProfilePageViewSet(PageViewSet):
    def get_queryset(self, *args, **kwargs):
        qs = Page.objects.filter(author_id=self.kwargs["accounts_pk"])
        return qs

    # TODO 질문지 3개 이상 작성 시 과금
    def perform_create(self, serializer):
        if self.kwargs["accounts_pk"] == str(self.request.user.pk):
            serializer.save(author=self.request.user)
            return super().perform_create(serializer)
        else:
            raise ValidationError("현재 프로필 유저만 작성할 수 있습니다.")


class QuestionViewSet(viewsets.ModelViewSet):
    """
            # 질문(questions) API
            ---
            # Allow Method GET, POST
            # /pages/{page_pk}/questions/
            ---
            # Allow Method RETRIEVE(GET), PUT(사용X), PATCH, DELETE
            # /pages/{page_pk}/questions/{id}/
            ---
            # request
            # POST, PATCH
                - title : STRING
                - content : STRING
            ---
            # response
            # /pages/{page_pk}/questions/
            # GET
                - "count": int,
                - "next": null,
                - "previous": null,
                - "results": [
                    {
                        "id": int,
                        "title": STRING,
                        "content": STRING,
                        "created_at": "2020-06-15T21:09:16.630261+09:00"
                    }
                ]

            # /pages/{page_pk}/questions/{id}/
                - "id": int,
                - "title": STRING,
                - "content": STRING,
                - "created_at": "2020-06-15T21:09:16.630261+09:00"
    """

    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    pagination_class = MyPagination

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(page__pk=self.kwargs["page_pk"])
        return qs

    # TODO 질문 3개이상 할 시 validation 적용
    def perform_create(self, serializer):
        page = get_object_or_404(Page, pk=self.kwargs["page_pk"])
        if page.author == self.request.user:
            serializer.save(author=self.request.user, page=page)
            return super().perform_create(serializer)
        else:
            raise ValidationError("질문지 작성자만 질문을 생성할 수 있습니다.")

    def perform_update(self, serializer):
        question = self.get_object()
        comment = Comments.objects.filter(question_id=self.kwargs["pk"]).all().count()
        if question.author == self.request.user and comment < 1:
            serializer.save()
            return super().perform_update(serializer)
        else:
            raise ValidationError("댓글이 등록된 질문 및 질문 작성자가 아닐 시 수정할 수 없습니다.")

    def perform_destroy(self, instance):
        if instance.author == self.request.user:
            instance.delete()
        else:
            raise ValidationError("질문 작성자만 질문을 삭제할 수 있습니다.")


class CommentViewSet(viewsets.ModelViewSet):
    """
            # 댓글(comments) API
            ---
            # Allow Method GET, POST
            # /pages/{page_pk}/questions/{question_id}/comments/
            ---
            # Allow Method RETRIEVE(GET), PUT(사용X), PATCH, DELETE
            # /pages/{page_pk}/questions/{question_id}/comments/{id}/
            ---
            # Allow Method GET, POST=201 contentX, DELETE=204
            # /pages/{page_pk}/questions/{question_id}/comments/{id}/like
            # /pages/{page_pk}/questions/{question_id}/comments/{id}/unlike
            ---
            # request
            # POST, PATCH
                - text : STRING
            ---
            # response
            # /pages/{page_pk}/questions/{question_id}/comments/
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
                        "text": STRING,
                        "is_like": Boolean,
                        "is_unlike": Boolean,
                        "like_count": Int or String(숫자),
                        "unlike_count": Int or String(숫자),
                        "is_mento": Boolean
                        "created_at": "2020-06-15T21:09:16.630261+09:00"
                    }
                ]

            # /pages/{page_pk}/questions/{id}/
                - "id": int,
                - "author": {
                            "pk": int,
                            "username": STRING,
                            "user_image": STRING
                        },
                - "text": STRING,
                - "is_like": Boolean or String(true or false),
                - "is_unlike": Boolean or String(true or false),
                - "like_count": Int or String(숫자),
                - "unlike_count": Int or String(숫자),
                - "is_mento": Boolean or String(true or false),
                - "created_at": "2020-06-15T21:09:16.630261+09:00"

            # /pages/{page_pk}/questions/{question_id}/comments/{id}/like
                - "likes": [
                        {
                            "id": int,
                            "username": STRING,
                            "user_image": STRING
                        }, ...
                    ]
    """

    queryset = Comments.objects.all().select_related("author")
    serializer_class = CommentsSerializer

    # TODO Comment 좋아요 싫어요 적용될 시 보여질지 말지 고민 듕
    def get_queryset(self):
        # timesince = timezone.now() - timedelta(days=3)
        qs = super().get_queryset()
        qs = qs.filter(question__pk=self.kwargs["question_pk"])
        # qs = qs.filter(created_at__gte=timesince)
        return qs

    def perform_create(self, serializer):
        question = get_object_or_404(Question, pk=self.kwargs["question_pk"])
        if self.request.user.is_mento or question.author == self.request.user:
            serializer.save(author=self.request.user, question=question)
            return super().perform_create(serializer)
        else:
            raise ValidationError("멘토로 등록된 인원만 댓글을 작성할 수 있습니다.")

    def perform_update(self, serializer):
        comment = self.get_object()
        if self.request.user == comment.author:
            serializer.save()
            return super().perform_create(serializer)
        else:
            raise ValidationError("댓글을 작성한 유저만 수정할 수 있습니다.")

    def perform_destroy(self, instance):
        question = get_object_or_404(Question, pk=self.kwargs["question_pk"])
        if instance.author == self.request.user or question.author == self.request.user:
            instance.delete()
        else:
            raise ValidationError("질문지 작성자 및 댓글을 작성한 유저만 삭제할 수 있습니다.")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    @action(detail=True, methods=["GET", "POST"])
    def like(self, request, *args, **kwargs):
        comment = self.get_object()
        user = self.request.user

        if request.method == "POST":
            if comment.unlike_user_set.filter(pk=user.pk).exists():
                comment.unlike_user_set.remove(user)
            elif comment.like_user_set.filter(pk=user.pk).exists():
                comment.like_user_set.remove(user)
                return Response(status.HTTP_204_NO_CONTENT)
            comment.like_user_set.add(user)
            return Response(status.HTTP_201_CREATED)
        else:
            like_user = comment.like_user_set.all()
            like_user = like_user.values()
            like_user_list = []

            # TODO 리팩토링 필요 ex Serializer 이용
            for i in range(len(like_user)):
                data = {}
                data["id"] = like_user[i]["id"]
                data["username"] = like_user[i]["username"]
                data["user_image"] = like_user[i]["user_image"]
                like_user_list.append(data)
            return Response({"likes": like_user_list}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["GET", "POST"])
    def unlike(self, request, *args, **kwargs):
        comment = self.get_object()
        user = self.request.user

        if request.method == "POST":
            if comment.like_user_set.filter(pk=user.pk).exists():
                comment.like_user_set.remove(user)
            elif comment.unlike_user_set.filter(pk=user.pk).exists():
                comment.unlike_user_set.remove(user)
                return Response(status.HTTP_204_NO_CONTENT)
            comment.unlike_user_set.add(user)
            return Response(status.HTTP_201_CREATED)
        else:
            unlike_user = comment.unlike_user_set.all()
            unlike_user = unlike_user.values()
            unlike_user_list = []

            # TODO 리팩토링 필요
            for i in range(len(unlike_user)):
                data = {}
                data["id"] = unlike_user[i]["id"]
                data["username"] = unlike_user[i]["username"]
                data["user_image"] = unlike_user[i]["user_image"]
                unlike_user_list.append(data)
            return Response({"unlikes": unlike_user_list}, status=status.HTTP_200_OK)
