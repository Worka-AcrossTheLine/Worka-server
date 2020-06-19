from django.conf import settings
from django.db import models


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Page(TimestampedModel):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="my_question", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=100)
    tags = models.ManyToManyField("Tag", blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-id"]


class Question(TimestampedModel):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["id"]


class Comments(TimestampedModel):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="question_comment_author",
        on_delete=models.CASCADE,
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField()
    like_user_set = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="like_comment_set"
    )
    unlike_user_set = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="unlike_comment_set"
    )

    def __str__(self):
        return f"{self.author}님이 작성한 댓글 {self.text}입니다."

    class Meta:
        ordering = ["id"]


class Tag(TimestampedModel):
    name = models.CharField(max_length=50, unique=True, primary_key=True)

    def __str__(self):
        return self.name
