from django.contrib import admin
from .models import Company, Mbti, User

# Register your models here.


@admin.register(Company, Mbti, User)
class UserAdmin(admin.ModelAdmin):
    pass
