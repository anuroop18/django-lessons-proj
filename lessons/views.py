import logging
from django.http import (Http404, HttpResponseBadRequest)
from django.shortcuts import render
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.db.models import Count

from lessons.models import Subscription
from lessons.forms import SubscribeForm
from lessons.models import Lesson
from taggit.models import Tag


logger = logging.getLogger(__name__)


ITEMS_PER_PAGE = 10


def handler500(request):
    return render(request, "lessons/500.html")


def index(request):
    """
        Landing page will list published lessons
        ordered by update_at (DESC)
    """
    if request.method != 'GET':
        return HttpResponseBadRequest()

    lessons = Lesson.objects.filter(live=True).order_by('-first_published_at')
    q = request.GET.get('q', None)

    if q:
        lessons = lessons.filter(title__icontains=q)

    paginator = Paginator(lessons, ITEMS_PER_PAGE)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'lessons/index.html',
        {
            'lessons': page_obj.object_list,
            'tags': Lesson.tags.most_common(),
            'page_obj': page_obj,
            'page_number': int(page_number),
            'paginator': paginator
        }
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
