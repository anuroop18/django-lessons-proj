import logging
from django.conf import settings
from django.http import (Http404, HttpResponseBadRequest)
from django.shortcuts import render
from django.views.generic import TemplateView
from django.core.paginator import Paginator

from lessons.models import (Subscription, Contact)
from lessons.forms import (SubscribeForm, ContactForm)
from lessons.models import (Lesson, Course)
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
    courses = Course.objects.order_by(
        '-first_published_at'
    )

    return render(
        request,
        'lessons/index.html',
        {
            'lessons': page_obj.object_list,
            'courses': courses,
            'tags': Tag.objects.order_by('name'),
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

    courses = Course.objects.order_by(
        '-first_published_at'
    )

    return render(
        request,
        'lessons/lesson.html',
        {
            'page': lesson,
            'courses': courses
        }
    )


class PageView(TemplateView):

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        courses = Course.objects.order_by(
            '-first_published_at'
        )
        context['courses'] = courses
        context['website'] = settings.WEBSITE
        context['service_name'] = settings.SERVICE_NAME
        context['email'] = settings.SERVICE_EMAIL

        return context


def subscribe(request):

    if request.method == 'POST':
        form = SubscribeForm(request.POST)
        if form.is_valid():
            subscribe = Subscription(
                email=form.cleaned_data['email'],
            )
            subscribe.save()
            return render(request, 'lessons/thankyou.html')
    else:
        form = SubscribeForm()

    courses = Course.objects.order_by(
        '-first_published_at'
    )

    return render(
        request,
        'lessons/subscribe.html',
        {
            'form': form,
            'courses': courses
        }
    )


def contact(request):

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = Contact(
                email=form.cleaned_data['email'],
                subject=form.cleaned_data['subject'],
                text=form.cleaned_data['text']
            )
            contact.save()
            return render(request, 'lessons/contact_thankyou.html')
    else:
        form = ContactForm()

    courses = Course.objects.order_by(
        '-first_published_at'
    )

    return render(
        request,
        'lessons/contact.html',
        {
            'form': form,
            'courses': courses
        }
    )
