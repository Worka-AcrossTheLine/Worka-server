from rest_framework import permissions, viewsets, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter
from .serializers import PostSerializer, CommentSerializer, AuthorSerializer
from .models import Post, Comment
from .permissions import IsOwnerOrReadOnly


# from django_filters.rest_framework import DjangoFilterBackend


class FeedViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().select_related("author").prefetch_related("likes")
    serializer_class = PostSerializer
    permission_classes = (IsOwnerOrReadOnly, permissions.IsAuthenticatedOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        return super().perform_create(serializer)

    def get_queryset(self):
        user = self.request.user
        following_users = user.following.all()  # user 모델 대입하세요
        queryset = Post.objects.all().filter(author__in=following_users)
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class CommentView(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (
        IsOwnerOrReadOnly,
        permissions.IsAuthenticatedOrReadOnly,
    )

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
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        post_id = self.kwargs["post_id"]
        queryset = Post.objects.get(pk=post_id).likes.all()
        return queryset


class All(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (permissions.AllowAny,)
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
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        return Post.objects.filter(tags__slug=self.kwargs.get("slug"))

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context
