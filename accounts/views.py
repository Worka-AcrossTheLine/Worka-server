from datetime import date, timedelta, datetime

from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework_jwt.settings import api_settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import exceptions, status
from rest_framework.generics import DestroyAPIView, get_object_or_404, UpdateAPIView
from rest_framework.permissions import AllowAny

from .models import Mbti
from .serializers import (
    SignupSerializer,
    UserSerializer,
    ChangePasswordSerializer,
    ChangeUsernameSerializer,
)


# Create your views here.


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
        data["username"] = user.username
        data["mbti"] = user.mbti
        data["point"] = user.point
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
    mbti = request.data.get("mbti")
    response = Response()

    if (username is None) or (password is None):
        raise exceptions.AuthenticationFailed("Required username and password")

    user = get_user_model().objects.get(username=username)
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

    user = get_user_model().objects.get(pk=request.user.pk)
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
