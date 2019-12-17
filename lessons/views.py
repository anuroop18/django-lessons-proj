from django.http import Http404
from django.shortcuts import render
from lessons.models import Lesson
from django.views.generic import TemplateView


def index(request):
    """
        Landing page will list published lessons
        ordered by update_at (DESC)
    """
    lessons = Lesson.objects.filter(
        published=True
    ).order_by('-updated_at')

    return render(
        request,
        'lessons/index.html',
        {'lessons': lessons}
    )


def lesson(request, id):

    try:
        lesson = Lesson.objects.get(id=id)
    except Lesson.DoesNotExist:
        raise Http404("Lesson not found")

    return render(
        request,
        'lessons/lesson.html',
        {'lesson': lesson}
    )


class PageView(TemplateView):
    pass
