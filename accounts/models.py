from datetime import date

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MinLengthValidator
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    UserManager,
)
from django.utils import timezone

username_length = MinLengthValidator(5, "유저명을 5글자 이상 입력해주세요")


class Company(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to="company")


class Mbti(models.Model):
    title = models.CharField(max_length=4)
    job = models.CharField(max_length=50)

    def __str__(self):
        return self.title


class User(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()

    objects = UserManager()

    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(
        "username",
        max_length=16,
        blank=False,
        unique=True,
        help_text=(
            "Required. 50 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator, username_length],
    )
    # birth_date = models.DateField(
    #     auto_now=False, null=False, blank=False, default=timezone.now()
    # )
    point = models.PositiveIntegerField(default=30)
    user_image = models.ImageField(blank=True, upload_to="accounts/userImage/%Y/%m/&d")
    follower = models.ManyToManyField(
        "self", blank=True, related_name="following", symmetrical=False
    )
    comments = models.CharField(max_length=50, blank=True)
    mbti = models.ForeignKey(Mbti, null=True, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, null=True, on_delete=models.CASCADE)

    is_mento = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = [
        "email",
    ]

    @property
    def age(self):
        today = date.today()
        try:
            birthday = self.birth_date.replace(year=today.year)
        except ValueError:
            birthday = self.birth_date.replace(
                year=today.year, month=self.birth_date.month + 1, day=1
            )
        if birthday > today:
            return today.year - self.birth_date.year - 1
        else:
            return today.year - self.birth_date.year
