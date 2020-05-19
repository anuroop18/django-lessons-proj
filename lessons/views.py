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
from django.contrib import messages
from taggit.models import Tag
from allauth.account.views import LoginView

from lessons.forms import (SubscribeForm, ContactForm)
from lessons.models import (
    Lesson,
    Course,
    LessonGroup,
    Subscription,
    Contact,
    PRO
)
from lessons.payments.stripe import (
    LessonsPlan,
    UserProfile,
    upgrade_customer,
    create_payment_intent,
    create_payment_subscription,
)
from lessons.payments.utils import (
    login_with_pro,
    upgrade_with_pro,
)


logger = logging.getLogger(__name__)


ITEMS_PER_PAGE = 10


def handler500(request):
    return render(request, "lessons/500.html")


class LessonLoginView(LoginView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method != 'GET':
            return context

        lesson_ord = self.request.GET.get('lesson-order', False)
        if not lesson_ord:
            return context

        try:
            lesson = Lesson.objects.get(order=lesson_ord)
        except Lesson.DoesNotExist:
            logger.error(
                f"Failed to get lesson with #{lesson_ord}"
            )
            return context

        context['lesson'] = lesson
        context['redirect_field_value'] = lesson.get_absolute_url

        return context


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

    user = request.user

    if lesson.lesson_type == PRO and not user.is_authenticated:
        return login_with_pro(lesson_order=order)
    elif lesson.lesson_type == PRO and user.is_authenticated:
        if user.profile and not user.profile.is_pro_user():
            # means an authenticated user which is not PRO
            # wants to access a PRO lesson => he will be redirected
            # to upgrade view with lesson_ord argument
            return upgrade_with_pro(lesson_order=order)

    view = request.GET.get('view', 'lesson')

    if view == 'lesson':
        template_name = 'lessons/lesson.html'
    else:
        template_name = 'lessons/lesson_within_course.html'

    course = None
    lesson_group = None

    if view == 'course':
        if lesson.lesson_groups.count() > 0:
            lesson_group = lesson.lesson_groups.first()
            course = lesson_group.course
            similar_lessons = []
            lesson_groups = LessonGroup.objects.filter(
                course=course
            ).order_by('order')
            next_item = lesson_group.get_next_lesson_group_obj()
            prev_item = lesson_group.get_prev_lesson_group_obj()
    else:
        lesson_groups = []
        similar_lessons = [
            sim_lesson.post
            for sim_lesson in lesson.similar_lessons.all()
        ]
        next_item = lesson.get_next_lesson_obj()
        prev_item = lesson.get_prev_lesson_obj()

    return render(
        request,
        template_name,
        {
            'page': lesson,
            'course': course,
            'lesson_group': lesson_group,
            'similar_lessons': similar_lessons,
            'all_course_lessons': lesson_groups,
            'next_item': next_item,
            'prev_item': prev_item
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
def trigger_error(request):
    division_by_zero = 1 / 0  # noqa


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
    lesson_ord = request.GET.get('lesson-order', False)

    if not lesson_ord:
        return render(request, 'lessons/upgrade.html')

    try:
        lesson = Lesson.objects.get(order=lesson_ord)
    except Lesson.DoesNotExist:
        logger.error(
            f"Failed to get lesson with #{lesson_ord}"
        )
        return render(request, 'lessons/upgrade.html')

    context = {}
    context['lesson'] = lesson

    return render(
        request,
        'lessons/upgrade.html',
        context
    )


@require_POST
@login_required
def checkout(request):
    payment_method = request.POST.get('payment_method', 'card')
    automatic = request.POST.get('automatic', False)
    lesson_plan = LessonsPlan(
        plan_id=request.POST.get('plan', 'm'),
        automatic=automatic

    )
    context = {}

    if payment_method == 'card':
        payment_intent = create_payment_intent(
            lesson_plan=lesson_plan
        )
        context['lesson_plan'] = lesson_plan
        context['stripe_plan_id'] = lesson_plan.stripe_plan_id
        context['secret_key'] = payment_intent.client_secret
        context['customer_email'] = request.user.email
        context['STRIPE_PUBLISHABLE_KEY'] = settings.STRIPE_PUBLISHABLE_KEY
        context['payment_intent_id'] = payment_intent.id
        context['automatic'] = automatic

        return render(request, 'lessons/payments/card.html', context)
    elif payment_method == 'paypal':
        return render(
            request,
            'lessons/payments/paypal.html'
        )
    else:
        messages.add_message(
            request,
            messages.ERROR,
            "Unknown payment method, please try again."
        )

    return render(request, 'lessons/upgrade.html')


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


login_view = LessonLoginView.as_view()
