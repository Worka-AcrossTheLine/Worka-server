from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

User = get_user_model()


class UserUpdateSerializer(serializers.Serializer):
    model = User


class UserDescriptionSerializer(UserUpdateSerializer):
    description = serializers.CharField(required=True)


class UserImageSerializer(serializers.ModelSerializer):
    user_image = serializers.ImageField(max_length=None, allow_empty_file=False)

    class Meta:
        model = User
        fields = [
            "pk",
            "username",
            "user_image",
        ]


class AuthorSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "pk",
            "username",
            "user_image",
        ]


class ChangePasswordSerializer(UserUpdateSerializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "pk",
            "username",
            "user_image",
        ]


class SignupSerializer(serializers.ModelSerializer):
    queryset = ""
    password = serializers.CharField(write_only=True)

    def save(self, **kwargs):
        user = User.objects.create(
            email=self.validated_data["email"],
            username=self.validated_data["username"],
        )

        if not len(self.validated_data["password"]) < 8:
            user.set_password(self.validated_data["password"])
            user.save()
            return user
        else:
            raise ValidationError("패스워드를 8글자 이상 입력해주세요")

    class Meta:
        model = User
        fields = [
            "pk",
            "email",
            "username",
            "password",
        ]


class UserSerializer(serializers.ModelSerializer):
    mento = serializers.SerializerMethodField("mento_count")
    mentiee = serializers.SerializerMethodField("mentiee_count")
    mbti = serializers.SerializerMethodField("mbti_field")

    def mento_count(self, user):
        return user.following.count()

    def mentiee_count(self, user):
        return user.follower.count()

    def mbti_field(self, user):
        if user.mbti is not None:
            return user.mbti.title

    class Meta:
        model = User
        fields = [
            "pk",
            "username",
            "user_image",
            "mento",
            "mentiee",
            "mbti",
            "description",
        ]


class ChangeUsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
        ]
