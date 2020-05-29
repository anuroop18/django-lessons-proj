import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import Signal, receiver

from .models import UserProfile
from .payments.plans import ANNUAL_AMOUNT, MONTHLY_AMOUNT

checkout_open = Signal()
checkout_in_progress = Signal()
checkout_complete_error = Signal()
checkout_complete_success = Signal()
checkout_webhook_in_progress = Signal()

logger = logging.getLogger(__name__)

DJANGO_LESSONS_NOTIFY_EMAIL = 'DJANGO_LESSONS_NOTIFY_EMAIL'


def notify(title, text):

    if not hasattr(settings, DJANGO_LESSONS_NOTIFY_EMAIL):
        logger.error(f"{DJANGO_LESSONS_NOTIFY_EMAIL} not defined")
    else:
        send_mail(
            title,
            text,
            settings.DJANGO_LESSONS_NOTIFY_EMAIL,
            [settings.DJANGO_LESSONS_NOTIFY_EMAIL],
            fail_silently=True,
        )


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    # update user profile
    if created:
        UserProfile.objects.create(
            user=instance
        )


@receiver(checkout_open)
def checkout_open_handler(sender, **kwargs):
    """
    Sent when user initiates a checkout process.
    kwargs:
        * payment_method - string - card, paypal
        * user - django.contrib.auth.models.User
        * lesson_plan - lessons.payments.plans.LessonsPlan
    """
    payment_method = kwargs.get('payment_method', False)
    user = kwargs.get('user', False)
    lesson_plan = kwargs.get('lesson_plan', False)
    text = ""
    if payment_method:
        text += f" PM={payment_method},"

    if user:
        text += f" email={user.email},"

    if lesson_plan:
        if lesson_plan.amount == MONTHLY_AMOUNT:
            text += " lesson_plan amount=19.95 USD"
        elif lesson_plan.amount == ANNUAL_AMOUNT:
            text += " lesson_plan amount=199.50 USD"
    notify(
        title=f"[{payment_method}] Checkout Open",
        text=text
    )


@receiver(checkout_in_progress)
def checkout_in_progress_handler(sender, **kwargs):
    """
    Sent when user initiates a checkout process.
    kwargs:
        * payment_method - string - card, paypal
        * user - django.contrib.auth.models.User
        * lesson_plan - lessons.payments.plans.LessonsPlan
    """
    payment_method = kwargs.get('payment_method', False)
    user = kwargs.get('user', False)
    lesson_plan = kwargs.get('lesson_plan', False)
    text = ""
    if payment_method:
        text += f" PM={payment_method},"

    if user:
        text += f" email={user.email},"

    if lesson_plan:
        text += f" lesson_plan amount={lesson_plan.amount}"

    notify(
        title=f"[{payment_method}] Checkout In Progress",
        text=text
    )


@receiver(checkout_complete_error)
def checkout_complete_error_handler(sender, **kwargs):
    email = kwargs.get('email', False)
    message = kwargs.get('message', False)
    text = f"sender={sender},"

    if email:
        text += f" email={email},"
    if message:
        text += f" message={message}"

    notify(
        title="[PAYMENT ERROR]",
        text=text
    )


@receiver(checkout_complete_success)
def checkout_complete_success_handler(sender, **kwargs):
    email = kwargs.get('email', False)
    message = kwargs.get('message', False)
    text = f"sender={sender},"

    if email:
        text += f" email={email},"
    if message:
        text += f" message={message}"

    notify(
        title="[PAYMENT SUCCESS]",
        text=text
    )


@receiver(checkout_webhook_in_progress)
def checkout_webhook_in_progress_handler(sender, **kwargs):
    email = kwargs.get('email', False)
    message = kwargs.get('message', False)
    text = f"sender={sender},"

    if email:
        text += f" email={email},"
    if message:
        text += f" message={message}"

    notify(
        title="[payment in progress]",
        text=text
    )
