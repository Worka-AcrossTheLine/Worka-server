from django.contrib import admin
from .models import Mbti, User

# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(Mbti)
class MbtiAdmin(admin.ModelAdmin):
    pass
