import logging
import stripe

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.conf import settings
from django.http import (Http404, HttpResponseBadRequest, HttpResponse)
from django.shortcuts import render
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt

from lessons.models import (Subscription, Contact)
from lessons.forms import (SubscribeForm, ContactForm)
from lessons.models import (Lesson, Course)
from lessons.payments import (
    LessonsPlan,
    UserProfile,
    upgrade_customer,
    create_payment_intent,
    create_payment_subscription,
)
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

    lesson_type = request.GET.get('ltype', False)

    lessons = Lesson.objects.filter(live=True).order_by('-first_published_at')
    q = request.GET.get('q', None)

    if q:
        lessons = lessons.filter(title__icontains=q)

    if lesson_type:
        lessons = lessons.filter(lesson_type=lesson_type)

    paginator = Paginator(lessons, ITEMS_PER_PAGE)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'lessons/index.html',
        {
            'lessons': page_obj.object_list,
            'tags': Tag.objects.order_by('name'),
            'page_obj': page_obj,
            'page_number': int(page_number),
            'paginator': paginator,
            'current_lesson_type': lesson_type
        }
    )


def lesson(request, order, slug):
    """
    One lesson can be viewed in two different ways:

        (1) as independent lesson
        (2) as part of one course

    As (1) it is well, independent. And it is not really
    important to jump to next in order lesson or not.
    It is more important in this conetxt to display 'related lessons'.

    As (2) this lesson is within logical sequence of group of lessons
    - a course.
    In this context, lesson title from within a course may override
    the title of the lesson.

    E.g. L#18, lesson.title = Django Deployment from Zero to Hero Part 1
         L#19, lesson.title = Django Deployment from Zero to Hero Part 2
         L#20, lesson.title = Django Deployment from Zero to Hero Part 3

    Within course, those lessons will be titled differently:
        course.title = Django Deployment from Zero to Hero

         lesson#1 - Setup VPS host
         lesson#2 - Setup Nginx
         lesson#3 - Prepare Database

    where lesson#1 is same 'thing' as L#18
          lesson#2 is same 'thing' as L#19.

    they are just within different context.

    Long story short, if user clicks on lesson from course view - lesson
    will be displayed differently - as lesson within course.
    To switch between views - pass http parameter view = course | lesson
    """
    try:
        lesson = Lesson.objects.get(order=order)
    except Lesson.DoesNotExist:
        logger.warning(f"Lesson #{order} not found")
        raise Http404("Lesson not found")

    view = request.GET.get('view', 'lesson')

    if view == 'lesson':
        template_name = 'lessons/lesson.html'
    else:
        template_name = 'lessons/lesson_within_course.html'

    course = None
    if lesson.lesson_groups.count() > 0:
        lesson_group = lesson.lesson_groups.first()
        course = lesson_group.course

    return render(
        request,
        template_name,
        {
            'page': lesson,
            'course': course,
            'lesson_group': lesson_group
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

    return render(
        request,
        'lessons/subscribe.html',
        {
            'form': form,
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

    return render(
        request,
        'lessons/contact.html',
        {
            'form': form,
        }
    )


@login_required
def user_profile(request):

    user = request.user

    if hasattr(user, 'profile'):
        user_profile = user.profile
    else:
        user_profile = UserProfile(
            user=user,
        )
        user_profile.save()

    is_pro = False

    if user_profile:
        is_pro = user_profile.is_pro_user()

    return render(
        request,
        'account/profile.html',
        {
            'user_profile': user_profile,
            'is_pro': is_pro
        }
    )


@login_required
def upgrade(request):
    logger.info("upgrade")
    return render(request, 'lessons/upgrade.html')


@login_required
def checkout(request):
    # accepts only GET and POST
    # GET
    if request.method == 'GET':

        payment_method = request.GET.get('payment_method', 'card')

        # paypal coming soon...
        if payment_method == 'paypal':
            return render(
                request,
                'lessons/checkout/paypal.html'
            )

        lesson_plan = LessonsPlan(
            request.GET.get('plan', False)
        )

        secret_key = create_payment_intent(
            lesson_plan=lesson_plan
        )
        return render(
            request,
            'lessons/checkout/card.html',
            {
                'plan_id': lesson_plan.id,
                'secret_key': secret_key,
                'customer_email': request.user.email,
                'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY
            }
        )

    if request.method != 'POST':
        return HttpResponseBadRequest()

    lesson_plan = LessonsPlan(
        request.POST.get('plan_id', False)
    )

    # POST
    create_payment_subscription(
        email=request.user.email,
        lesson_plan=lesson_plan,
        payment_method_id=request.POST.get('payment_method_id', False)
    )

    return render(request, 'lessons/checkout/thank_you.html')


@require_POST
@csrf_exempt
def webhooks(request):
    logger.info("Stripe webhook received")

    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SIGNING_KEY
        )
        logger.info("Event constructed correctly")
    except ValueError:
        # Invalid payload
        logger.warning("Invalid Payload")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        logger.warning("Invalid signature")
        return HttpResponse(status=400)

    # Handle the event
    if event.type == 'invoice.payment_succeeded':
        # ... handle other event types
        upgrade_customer(invoice=event.data.object)
    else:
        # Unexpected event type
        return HttpResponse(status=400)

    return HttpResponse(status=200)

