from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from lessons.models import (User, Lesson, Subscribtion)


class LessonAdmin(admin.ModelAdmin):
    save_on_top = True

    list_display = (
        'order',
        'title',
        'public'
    )
    exclude = ('user')

    def save_model(self, request, obj, form, change):
        admin_user = User.objects.get(is_superuser=True)
        obj.user = admin_user
        if not change:
            obj.order = Lesson.next_order()
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        super().delete_model(request, obj)


class SubscribtionAdmin(admin.ModelAdmin):
    pass


admin.site.register(User, UserAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Subscribtion, SubscribtionAdmin)

