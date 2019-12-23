import logging
from django.http import (Http404, HttpResponseBadRequest)
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
    logger.info(f"I am lessons APP:INFO: index view accessed")

    if request.method != 'GET':
        return HttpResponseBadRequest()

    tag_id = request.GET.get('tag_id', None)
    lessons = Lesson.obj.published().tagged(tag_id)
    tags = Tag.objects.all().order_by('name')

    return render(
        request,
        'lessons/index.html',
        {'lessons': lessons, 'tags': tags}
    )


def lesson(request, order, slug):
    try:
        lesson = Lesson.objects.get(order=order)
    except Lesson.DoesNotExist:
        logger.warning(f"Lesson #{order} not found")
        raise Http404("Lesson not found")

    return render(
        request,
        'lessons/lesson.html',
        {'lesson': lesson}
    )


class PageView(TemplateView):
    pass
