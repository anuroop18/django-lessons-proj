from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import Signal, receiver

from .models import UserProfile

checkout_open = Signal()
checkout_in_progress = Signal()
checkout_complete_error = Signal()
checkout_complete_success = Signal()
checkout_webhook_in_progress = Signal()


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
    pass


@receiver(checkout_in_progress)
def checkout_in_progress_handler(sender, **kwargs):
    """
    Sent when user initiates a checkout process.
    kwargs:
        * payment_method - string - card, paypal
        * user - django.contrib.auth.models.User
        * lesson_plan - lessons.payments.plans.LessonsPlan
    """
    pass


@receiver(checkout_complete_error)
def checkout_complete_error_handler(sender, **kwargs):
    pass


@receiver(checkout_complete_success)
def checkout_complete_success_handler(sender, **kwargs):
    pass


@receiver(checkout_webhook_in_progress)
def checkout_webhook_in_progress_handler(sender, **kwargs):
    pass
