import logging

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.conf import settings
from django.http import (Http404, HttpResponseBadRequest)
from django.shortcuts import render
from django.views.generic import TemplateView
from django.core.paginator import Paginator

from django.contrib import messages
from taggit.models import Tag
from allauth.account.views import LoginView

from .forms import (SubscribeForm, ContactForm)
from .models import (
    Lesson,
    Course,
    UserProfile,
    LessonGroup,
    Subscription,
    Contact,
    PRO
)
from .payments import plans
from .payments import stripe as my_stripe
from .payments.clients.stripe import stripe_client
from .payments.utils import (
    login_with_pro,
    upgrade_with_pro,
)


logger = logging.getLogger(__name__)

API_KEY = settings.STRIPE_SECRET_KEY

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
        lessons = lessons.search(q)

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
            'user': user,
            'user_profile': user_profile,
            'is_pro': is_pro,
            'automatic_renew': user_profile.is_with_automatic_renew
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


@login_required
def cancel_subscription(request):
    if request.method == 'POST':
        user = request.user
        subs_id = user.profile.stripe_subscription_id

        if subs_id:
            subs = my_stripe.Subscription(
                client=stripe_client,
                user=request.user
            )
            subs.cancel(subscription_id=subs.id)
            status = subs.status
            context = {
                'msg': status.message,
                'tag': status.tag,
                'title': status.title
            }
            return render(
                request,
                'lessons/payments/thank_you.html',
                context
            )

    return render(
        request,
        'lessons/cancel_subscription.html'
    )


@require_POST
@login_required
def checkout(request):
    payment_method = request.POST.get('payment_method', 'card')
    automatic = request.POST.get('automatic', False)
    lesson_plan = plans.LessonsPlan(
        plan_id=request.POST.get('plan', 'm'),
        automatic=automatic
    )
    context = {}

    if payment_method == 'card':
        context['lesson_plan'] = lesson_plan
        context['stripe_plan_id'] = lesson_plan.stripe_plan_id
        context['customer_email'] = request.user.email
        context['STRIPE_PUBLISHABLE_KEY'] = settings.STRIPE_PUBLISHABLE_KEY
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


@login_required
def thank_you(request):
    # useful for testing
    if request.method != 'GET':
        return HttpResponseBadRequest()

    context = {}
    context['msg'] = request.GET.get('msg', '')
    context['tag'] = request.GET.get('tag', '')
    context['title'] = request.GET.get('title', '')

    return render(
        request,
        'lessons/payments/thank_you.html',
        context
    )


@login_required
def card(request):
    payment_method_id = request.POST['payment_method_id']
    stripe_plan_id = request.POST['stripe_plan_id']
    automatic = request.POST['automatic']
    lesson_plan_id = request.POST['lesson_plan_id']

    if automatic == 'on':
        payment = my_stripe.RecurringPayment(
            client=stripe_client,
            user=request.user,
            stripe_plan_id=stripe_plan_id,
            payment_method_id=payment_method_id
        )

        payment.create_subscription()

        if payment.requires_action:
            return render(
                request,
                'lessons/payments/3dsec.html',
                payment.get_3ds_context
            )
    else:
        payment = my_stripe.OneTimePayment(
            client=stripe_client,
            user=request.user,
            lesson_plan_id=lesson_plan_id
        )
        payment.pay()

    status = payment.status
    context = {
        'msg': status.message,
        'tag': status.tag,
        'title': status.title
    }
    return render(
        request,
        'lessons/payments/thank_you.html',
        context
    )


login_view = LessonLoginView.as_view()
