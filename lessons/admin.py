from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from lessons.models import (User, Lesson)


class LessonAdmin(admin.ModelAdmin):
    pass


admin.site.register(User, UserAdmin)
admin.site.register(Lesson, LessonAdmin)

