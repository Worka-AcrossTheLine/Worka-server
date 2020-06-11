from django.contrib import admin
from .models import Company, Mbti, User, Mento

# Register your models here.


@admin.register(Company, Mbti, User, Mento)
class UserAdmin(admin.ModelAdmin):
    pass
