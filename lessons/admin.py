from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Contact, Course, Lesson, LessonGroup, Subscription


class ContactAdmin(admin.ModelAdmin):
    list_display = ('email', 'subject')


class SubscriptionAdmin(admin.ModelAdmin):
    pass


class CourseAdmin(admin.ModelAdmin):
    pass


class LessonAdmin(admin.ModelAdmin):
    pass


class LessonGroupAdmin(admin.ModelAdmin):
    pass


admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(LessonGroup, LessonGroupAdmin)
