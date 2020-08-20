from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MinLengthValidator
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    UserManager,
)

username_length_validator = MinLengthValidator(5, "유저명을 5글자 이상 입력해주세요")


class Company(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to="company")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "company"



class Mbti(models.Model):
    title = models.CharField(max_length=4)
    job = models.CharField(max_length=50)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "mbti"
        verbose_name = "MBTI"
        verbose_name_plural = verbose_name


class User(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()

    objects = UserManager()

    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(
        "username",
        max_length=16,
        blank=False,
        unique=True,
        validators=[username_validator, username_length_validator],
    )
    user_image = models.ImageField(blank=True, upload_to="accounts/userImage/%Y/%m/&d")
    follower = models.ManyToManyField(
        "self", blank=True, related_name="following", symmetrical=False
    )
    description = models.CharField(max_length=50, blank=True)
    mbti = models.ForeignKey(Mbti, null=True, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    is_mento = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = [
        "email",
    ]
