import logging

from allauth.account import signals as allauth_signals
from allauth.socialaccount import signals as allauth_social_signals
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import Signal, receiver

from .models import Contact, Subscription, UserProfile
from .payments.plans import ANNUAL_AMOUNT, MONTHLY_AMOUNT

checkout_open = Signal()
checkout_in_progress = Signal()
checkout_complete_error = Signal()
checkout_complete_success = Signal()
checkout_webhook_in_progress = Signal()
new_subscriber = Signal()
new_contact_message = Signal()

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
    else:
        text += "Empty PM"

    if user:
        text += f" email={user.email},"
    else:
        text += "Empty email"

    if lesson_plan:
        if lesson_plan.amount == MONTHLY_AMOUNT:
            text += " lesson_plan amount=19.95 USD"
        elif lesson_plan.amount == ANNUAL_AMOUNT:
            text += " lesson_plan amount=199.50 USD"
        else:
            text += f" Strange amount={lesson_plan.amount}"
    else:
        text += "Empty lesson_plan"

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
    else:
        text += "Empty PM"

    if user:
        text += f" email={user.email},"
    else:
        text += "Empty email"

    if lesson_plan:
        if lesson_plan.amount == MONTHLY_AMOUNT:
            text += " lesson_plan amount=19.95 USD"
        elif lesson_plan.amount == ANNUAL_AMOUNT:
            text += " lesson_plan amount=199.50 USD"
        else:
            text += f" Strange amount={lesson_plan.amount}"
    else:
        text += "Empty lesson_plan"

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
    else:
        text += "Empty email"

    if message:
        text += f" message={message}"
    else:
        text += "Empty message"

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
    else:
        text += "Empty email"

    if message:
        text += f" message={message}"
    else:
        text += "Empty message"

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
    else:
        text += "Empty email"

    if message:
        text += f" message={message}"
    else:
        text += "Empty message"

    notify(
        title="[payment in progress]",
        text=text
    )


@receiver(new_subscriber)
def new_subscriber_handler(sender, **kwargs):
    title = "New Subscriber"
    email = kwargs.get('email', False)
    text = f" sender={sender},"
    count = Subscription.objects.count()

    if email:
        text += f" email={email}"
    else:
        text += "Empty email"

    text += f" Total subscriptions count={count}"

    notify(
        title=title,
        text=text
    )


@receiver(new_contact_message)
def new_contact_message_handler(sender, **kwargs):
    title = "New Contact Message"
    email = kwargs.get('email', False)
    subject = kwargs.get('subject', False)
    text = f" sender={sender},"
    count = Contact.objects.count()

    if email:
        text += f" email={email},"
    else:
        text += "Empty email"

    if subject:
        text += f" subject={subject}"
    else:
        text += "Empty subject"

    text += f" Total Contacts count={count}"

    notify(
        title=title,
        text=text
    )


@receiver(allauth_signals.user_signed_up)
def user_signed_up_handler(sender, **kwargs):

    email = kwargs.get('email', False)
    text = f" email={email}, "
    count = User.objects.count()
    text += f" Total User count={count}"

    notify(
        title="New Sign Up",
        text=text
    )


@receiver(allauth_signals.password_reset)
def password_reset_handler(sender, **kwargs):

    email = kwargs.get('email', False)
    text = f" email={email}, "

    notify(
        title="Password Reset triggered",
        text=text
    )


@receiver(allauth_signals.password_changed)
def password_changed_handler(sender, **kwargs):

    email = kwargs.get('email', False)
    text = f" email={email}, "

    notify(
        title="Password Changed triggered",
        text=text
    )


@receiver(allauth_social_signals.pre_social_login)
def pre_social_login_handler(sender, **kwargs):

    text = " "
    count = User.objects.count()
    text += f" Total User count={count}"

    notify(
        title="New Social account activity",
        text=text
    )
