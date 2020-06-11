from datetime import date, timedelta, datetime
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_jwt.settings import api_settings

User = get_user_model()


class SignupSerializer(serializers.ModelSerializer):
    queryset = ""
    password = serializers.CharField(write_only=True)
    birth_date = serializers.DateField(write_only=True)
    point = serializers.IntegerField(read_only=True)
    mbti = serializers.CharField(read_only=True)

    def save(self, **kwargs):
        validate_date = date.today() + timedelta(days=-3600)

        if self.validated_data["birth_date"] <= validate_date:
            user = User.objects.create(
                email=self.validated_data["email"],
                username=self.validated_data["username"],
                birth_date=self.validated_data["birth_date"],
            )

            if not len(self.validated_data["password"]) < 8:
                user.set_password(self.validated_data["password"])
                user.save()
                return user
            else:
                raise ValidationError("패스워드를 8글자 이상 입력해주세요")
        else:
            raise ValidationError("생년월일을 올바르게 입력해주세요")

    class Meta:
        model = User
        fields = [
            "pk",
            "email",
            "username",
            "password",
            "birth_date",
            "point",
            "mbti",
        ]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "pk",
            "username",
            "point",
            "mbti",
        ]


class ChangePasswordSerializer(serializers.Serializer):
    model = get_user_model()
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class ChangeUsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            "username",
        ]
