import logging
from django.http import Http404
from django.shortcuts import render
from django.views.generic import TemplateView

from taggit.models import Tag

from lessons.models import Lesson


logger = logging.getLogger(__name__)


def index(request):
    """
        Landing page will list published lessons
        ordered by update_at (DESC)
    """

    # TODO: refactoring required
    lessons = Lesson.objects
    if request.method == 'GET':
        tag_id = request.GET.get('tag_id', None)
        if tag_id:
            try:
                tag = Tag.objects.get(id=tag_id)
                lessons = lessons.filter(tags__name__in=[tag.name])
            except Tag.DoesNotExist:
                logger.info(f"tag_id={tag_id} not found")

    lessons = lessons.filter(
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
