from django.contrib import admin
from .models import Post, PostTag


@admin.register(Post, PostTag)
class PostAdmin(admin.ModelAdmin):
    pass
