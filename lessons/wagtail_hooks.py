from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register)
from .models import (Lesson, LessonGroup, Course)


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

    list_display = (
        'order',
        'get_lesson',
        'get_course',
    )

    def get_course(self, obj):
        return obj.course

    def get_lesson(self, obj):
        return obj.lesson

    get_course.short_description = 'Course'
    get_course.admin_order_field = 'course__title'

    get_lesson.short_description = 'Lesson'
    get_lesson.admin_order_field = 'lesson__title'


class CourseAdmin(ModelAdmin):
    model = Course
    list_display = (
        'title',
        'live'
    )


# Now you just need to register your customised ModelAdmin class with Wagtail
modeladmin_register(LessonAdmin)
modeladmin_register(LessonGroupAdmin)
modeladmin_register(CourseAdmin)

