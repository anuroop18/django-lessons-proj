from django.shortcuts import render
from lessons.models import Lesson
from django.views.generic import TemplateView


def index(request):
    lessons = Lesson.objects.all().order_by('-updated_at')

    return render(
        request,
        'lessons/index.html',
        {'lessons': lessons}
    )


class PageView(TemplateView):
    pass
