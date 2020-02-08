import logging
from django.http import (Http404, HttpResponseBadRequest)
from django.shortcuts import render
from django.views.generic import TemplateView

from lessons.models import Subscription
from lessons.forms import SubscribeForm
from lessons.models import Lesson
from taggit.models import Tag


logger = logging.getLogger(__name__)


def handler500(request):
    return render(request, "lessons/500.html")


def index(request):
    """
        Landing page will list published lessons
        ordered by update_at (DESC)
    """
    if request.method != 'GET':
        return HttpResponseBadRequest()

    tags = Tag.objects.all().order_by('name')
    lessons = Lesson.objects.filter(live=True).order_by('-first_published_at')
    q = request.GET.get('q', None)

    if q:
        lessons = lessons.filter(title__icontains=q)

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
        {'page': lesson}
    )


class PageView(TemplateView):
    pass


def subscribe(request):

    if request.method == 'POST':
        form = SubscribeForm(request.POST)
        if form.is_valid():
            subscribe = Subscription(email=form.cleaned_data['email'])
            subscribe.save()
            return render(request, 'lessons/thankyou.html')
    else:
        form = SubscribeForm()

    return render(
        request,
        'lessons/subscribe.html',
        {'form': form}
    )
