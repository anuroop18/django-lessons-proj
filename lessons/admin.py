from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from lessons.models import (User, Lesson, Subscribtion)


class LessonAdmin(admin.ModelAdmin):
    list_display = (
        'order',
        'title',
        'public'
    )


class SubscribtionAdmin(admin.ModelAdmin):
    pass


admin.site.register(User, UserAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Subscribtion, SubscribtionAdmin)

