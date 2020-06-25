from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework_jwt.settings import api_settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import exceptions, status
from rest_framework.generics import (
    DestroyAPIView,
    get_object_or_404,
    UpdateAPIView,
    RetrieveAPIView,
)
from rest_framework.permissions import AllowAny

from post.models import Post
from post.serializers import PostSerializer
from question.models import Page
from question.serializers import PageSerializer
from .models import Mbti
from .serializers import (
    SignupSerializer,
    UserSerializer,
    ChangePasswordSerializer,
    ChangeUsernameSerializer,
    FollowSerializer,
    UserImageSerializer,
    UserCommentSerializer,
)

from password_generator import PasswordGenerator

from .tasks import send_tmp_password


# Create your views here.
class ProfilePage(RetrieveAPIView):
    """
            # 질문지(page) API
            ---
            # Allow Method GET, POST
            # /profile/{id}
            ---
            # response
                - "user": {
                        "pk": 1,
                        "username": "admin",
                        "user_image": null,
                        "mento": 0,
                        "mentiee": 0,
                        "mbti": null,
                        "is_me": true
                    },
                - "pages": [
                        {
                            "id": 2,
                            "author": {
                                "pk": 1,
                                "username": "admin",
                                "user_image": null
                            },
                            "title": "string",
                            "tags": [
                                "string"
                            ],
                            "questions": 0,
                            "created_at": "2020-06-15T23:11:18.447558+09:00"
                        },
                    ]
                    - "cards": [
                        {
                            "id": "2ffda24d-d27b-4728-930b-5de056838a11",
                            "author": {
                                "username": "admin",
                                "user_image": null
                            },
                            "images": null,
                            "text": "STRING",
                            "created_at": "2020-06-16",
                            "updated_at": "2020-06-16",
                            "number_of_likes": 0,
                            "number_of_comments": 0,
                            "tags": [
                                "STRING"
                            ]
                        }
                    ]

    """

    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        pages = Page.objects.filter(author_id=self.kwargs["pk"])
        cards = Post.objects.filter(author_id=self.kwargs["pk"])
        pages = PageSerializer(pages, many=True).data
        cards = PostSerializer(cards, many=True).data
        return Response({"user": serializer.data, "pages": pages, "cards": cards})

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


@api_view(["GET", "POST"])
def mento_user(request, *args, **kwargs):
    current_user = get_user_model().objects.get(pk=kwargs["accounts_pk"])
    request_user = get_user_model().objects.get(pk=request.user.pk)

    if request.method == "POST":
        if request_user != current_user:
            if not current_user.follower.filter(pk=request_user.pk).exists():
                current_user.follower.add(request_user)
                return Response(status=status.HTTP_201_CREATED)
            else:
                current_user.follower.remove(request_user)
                return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        if int(current_user.follower.filter(pk=request_user.pk).count()) > 0:
            follower = current_user.follower.filter(pk=request_user.pk)
            follower = FollowSerializer(follower, many=True).data
            return Response({"mento": follower}, status=status.HTTP_200_OK)
        else:
            raise ValidationError("멘토가 존재하지 않습니다.")


@api_view(["GET"])
def mentiee_user(request, *args, **kwargs):
    current_user = get_user_model().objects.get(pk=kwargs["accounts_pk"])

    if int(current_user.following.count()) > 0:
        following = current_user.following.all()
        following = FollowSerializer(following, many=True).data
        return Response({"mentiee": following}, status=status.HTTP_200_OK)
    else:
        raise ValidationError("멘티가 존재하지 않습니다.")


@api_view(["POST"])
@permission_classes([AllowAny])
def tmp_password(request):
    """
        # 임시 비밀번호 이메일 전송
            :param request:
                - email: String
                - username: String
            :return: 201
    """
    email = request.data.get("email")
    username = request.data.get("username")

    if (username is None) or (email is None):
        raise exceptions.AuthenticationFailed("Required email and username")

    user = get_object_or_404(get_user_model(), username=username, email=email)
    if user is None:
        raise exceptions.AuthenticationFailed("User not found")

    pwd = PasswordGenerator()
    new_pwd = pwd.generate()

    user.set_password(new_pwd)
    user.save()

    send_tmp_password.delay(user.email, user.username, new_pwd)
    print(user.email)

    return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def signup_view(request):
    """
            유저 회원가입 API
            ---
            # 내용
                - email : "STRING"
                - username : "STRING"
                - password : "STRING"
                - birth_date : "YYYY-mm-dd"
    """
    serializer = SignupSerializer(data=request.data)
    data = {}
    if serializer.is_valid():
        user = serializer.save()
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        data["token"] = token
        data["pk"] = user.pk
        data["username"] = user.username
        data["mbti"] = user.mbti
        return Response(data, status=status.HTTP_201_CREATED,)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteUserView(DestroyAPIView):
    """
        유저 삭제 API
        ---
        # JWT 토큰값만 보내주심 되용
    """

    model = get_user_model()
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        return get_user_model().objects.get(id=self.request.user.id)


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    """
            유저 로그인 API
            ---
            # 내용
                - username : "STRING"
                - password : "STRING"
    """
    username = request.data.get("username")
    password = request.data.get("password")

    response = Response()

    if (username is None) or (password is None):
        raise exceptions.AuthenticationFailed("Required username and password")

    user = get_object_or_404(get_user_model(), username=username)
    if user is None:
        raise exceptions.AuthenticationFailed("User not found")
    if not user.check_password(password):
        raise exceptions.AuthenticationFailed("Wrong password")

    user_data = UserSerializer(user).data

    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

    payload = jwt_payload_handler(user)
    token = jwt_encode_handler(payload)

    response.data = {
        "token": token,
        "user": user_data,
    }

    return response


@api_view(["PATCH"])
def tendency_view(request):
    """
            유저 mbti 업데이 API(JWT 필요)
            ---
            # 내용트
                - mbti : "STRING"
    """

    mbti = request.data.get("mbti")

    if mbti is None:
        raise ValidationError("mbti 값을 넣어주세요")

    user = get_object_or_404(get_user_model(), pk=request.user.pk)
    mbti = Mbti.objects.filter(title=mbti).first()

    user.mbti = mbti
    user.save()

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([AllowAny])
def forgot_username_view(request):
    """
            유저 이름보여주는 API
            ---
            # 내용
                - email : "STRING"
    """
    email = request.data.get("email")

    if email is None:
        raise ValidationError("올바른 Email 값을 넣어주세요")

    user = get_object_or_404(get_user_model(), email=email)
    username = UserSerializer(user).data["username"]

    if len(username) <= 8:
        username = username[0 : len(username) - 3] + "***"
    else:
        username = username[0 : len(username) - 4] + "****"
    return Response({"username": username}, status=status.HTTP_200_OK)


class ChangePassword(UpdateAPIView):
    model = get_user_model()
    serializer_class = ChangePasswordSerializer

    def get_object(self, queryset=None):
        user = self.request.user
        return user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not user.check_password(serializer.data.get("old_password")):
                return Response(
                    {"old_password": ["Wrong password"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.set_password(serializer.data.get("new_password"))
            user.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeUsername(UpdateAPIView):
    model = get_user_model()
    serializer_class = ChangeUsernameSerializer

    def get_object(self, queryset=None):
        user = self.request.user
        return user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if serializer.data.get("username") is None:
                raise ValidationError("유저명을 입력해주세요")
            user.username = serializer.data.get("username")
            user.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateUserImage(UpdateAPIView):
    model = get_user_model()
    serializer_class = UserImageSerializer

    def get_object(self, queryset=None):
        user = self.request.user
        return user

    def perform_update(self, serializer):
        user = self.get_object()
        if user == self.request.user:
            serializer.save()
            return super().perform_update(serializer)
        else:
            raise ValidationError("자신 이미지만 수정 가능합니다")


class UpateComment(UpdateAPIView):
    model = get_user_model()
    serializer_class = UserCommentSerializer

    def get_object(self, queryset=None):
        user = self.request.user
        return user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            comment = serializer.data.get("comment")
            if comment is None:
                raise ValidationError("Comment를 작성해주세요")
            user.comments = comment
            user.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
