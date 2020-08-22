from django.db import models
from django.conf import settings


class TimeStampedModel(models.Model):
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        abstract = True


class PostTag(TimeStampedModel):
    name = models.CharField(max_length=13, unique=True, primary_key=True, db_index=True)

    def __str__(self):
        return self.name


class Post(TimeStampedModel):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_posts"
    )
    images = models.ImageField(upload_to="post/%Y/%m/%d")
    text = models.TextField()
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="likers", blank=True, symmetrical=False
    )
    tags = models.ManyToManyField(PostTag, blank=True)

    class Meta:
        db_table = "post"
        ordering = [
            "-id",
        ]

    def __str__(self):
        return f"{self.author}'의 게시글입니다."
