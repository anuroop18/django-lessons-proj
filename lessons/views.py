from django.http import Http404
from django.shortcuts import render
from django.views.generic import TemplateView

from taggit.models import Tag

from lessons.models import Lesson


def index(request):
    """
        Landing page will list published lessons
        ordered by update_at (DESC)
    """
    lessons = Lesson.objects.filter(
        published=True
    ).order_by('-updated_at')

    tags = Tag.objects.all().order_by('name')

    return render(
        request,
        'lessons/index.html',
        {'lessons': lessons, 'tags': tags}
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
