from django.db import models
from django.conf import settings


class TimeStampedModel(models.Model):
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        abstract = True


class LinkTag(TimeStampedModel):
    name = models.CharField(max_length=50)


class Link(TimeStampedModel):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    tag = models.ManyToManyField(LinkTag, related_name="link_tag", blank=True)
    url = models.URLField()


class PostTag(TimeStampedModel):
    name = models.CharField(max_length=13, unique=True, primary_key=True)

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
        ordering = [
            "-id",
        ]

    def number_of_likes(self):
        if self.likes.count():
            return self.likes.count()
        else:
            return 0

    def __str__(self):
        return f"{self.author}'s post"
