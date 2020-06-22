import uuid
import os
from django.db import models
from django.conf import settings
from taggit.managers import TaggableManager
from taggit.models import GenericUUIDTaggedItemBase, TaggedItemBase


class UUIDTaggedItem(GenericUUIDTaggedItemBase, TaggedItemBase):
    class Meta:
        verbose_name = "Tag"


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


class Post(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_posts"
    )
    images = models.ImageField(
        upload_to="uploads/Post/%Y/%m/%d", blank=False, editable=False
    )
    text = models.TextField(max_length=900, blank=True)
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="likers", blank=True, symmetrical=False
    )
    tags = TaggableManager(through=UUIDTaggedItem)

    class Meta:
        ordering = ["-id"]

    def number_of_likes(self):
        if self.likes.count():
            return self.likes.count()
        else:
            return 0

    def __str__(self):
        return f"{self.author}'s post"


class Comment(TimeStampedModel):
    post = models.ForeignKey(
        "Post", on_delete=models.CASCADE, related_name="post_comments",
    )
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,)
    text = models.CharField(max_length=100)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author}'s comment"
