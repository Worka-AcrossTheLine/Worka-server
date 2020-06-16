from django.contrib import admin
from .models import Question, Comments, Tag, Page

# Register your models here.


@admin.register(Page, Question, Comments, Tag)
class QuestionAdmin(admin.ModelAdmin):
    pass
