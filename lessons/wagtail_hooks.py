from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register)
from .models import Lesson


class LessonAdmin(ModelAdmin):
    model = Lesson
    list_display = (
        'order',
        'title',
        'live'
    )
    search_fields = ('title',)


# Now you just need to register your customised ModelAdmin class with Wagtail
modeladmin_register(LessonAdmin)

