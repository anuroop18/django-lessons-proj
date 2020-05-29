from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import Signal, receiver

from .models import UserProfile

upgrade_open = Signal()
upgrade_in_progress = Signal()
upgrade_complete_error = Signal()
upgrade_complete_success = Signal()
pro_screencast_view_open = Signal()


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    # update user profile
    if created:
        UserProfile.objects.create(
            user=instance
        )


def upgrade_open_handler(sender, **kwargs):
    pass


def upgrade_in_progress_handler(sender, **kwargs):
    pass


def upgrade_complete_error_handler(sender, **kwargs):
    pass


def upgrade_complete_success_handler(sender, **kwargs):
    pass
