from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register)
from .models import (Lesson, LessonGroup)


class LessonAdmin(ModelAdmin):
    model = Lesson
    list_display = (
        'order',
        'title',
        'live'
    )
    search_fields = ('title',)


class LessonGroupAdmin(ModelAdmin):
    model = LessonGroup


# Now you just need to register your customised ModelAdmin class with Wagtail
modeladmin_register(LessonAdmin)
modeladmin_register(LessonGroupAdmin)

