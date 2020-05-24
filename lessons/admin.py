from django.contrib import admin
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from django.contrib.auth.admin import UserAdmin
from .models import (
    Subscription,
    Lesson,
    Course,
    LessonGroup,
    Contact
)


def notify_new_lesson(modeladmin, request, queryset):

    if queryset.count() == 1:
        just_one_lesson = True
    else:
        just_one_lesson = False

    context = {
        'lessons': queryset,
        'just_one_lesson': just_one_lesson
    }

    text_msg = render_to_string(
        "lessons/notify_subscribers/email.txt",
        context
    )
    html_msg = render_to_string(
        "lessons/notify_subscribers/email.html",
        context
    )

    subscribers_email_list = [
        obj.email for obj in Subscription.objects.all()
    ]

    if queryset.count() > 1:
        title = "New Lessons available"
    elif queryset.count() == 1:
        lesson = queryset.first()
        title = f"New Lesson Released - {lesson.order} {lesson.title}"
    msg = EmailMultiAlternatives(
        title,
        text_msg,
        settings.EMAIL_FROM,
        subscribers_email_list
    )
    msg.attach_alternative(html_msg, "text/html")
    msg.send()


notify_new_lesson.short_description = "Notify subscribers about sel. lessons"


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


#admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(LessonGroup, LessonGroupAdmin)


