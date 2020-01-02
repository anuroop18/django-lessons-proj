import logging
from django.http import (Http404, HttpResponseBadRequest)
from django.shortcuts import render
from django.views.generic import TemplateView

from taggit.models import Tag

from lessons.models import (Lesson, Subscribtion)
from lessons.forms import SubscribeForm


logger = logging.getLogger(__name__)


def index(request):
    """
        Landing page will list published lessons
        ordered by update_at (DESC)
    """
    if request.method != 'GET':
        return HttpResponseBadRequest()

    tag_id = request.GET.get('tag_id', None)
    q = request.GET.get('q', None)
    lessons = Lesson.obj.published().tagged(tag_id).search(title=q)
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


def subscribe(request):

    if request.method == 'POST':
        form = SubscribeForm(request.POST)
        if form.is_valid():
            subscribe = Subscribtion(email=form.cleaned_data['email'])
            subscribe.save()
            return render(request, 'lessons/thankyou.html')
    else:
        form = SubscribeForm()

    return render(
        request,
        'lessons/subscribe.html',
        {'form': form}
    )
