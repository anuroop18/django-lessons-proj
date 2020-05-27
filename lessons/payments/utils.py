import logging
from datetime import date, datetime, timedelta

from django.shortcuts import HttpResponseRedirect
from django.urls import reverse
from django.utils.http import urlencode
from lessons.models import UserProfile

logger = logging.getLogger(__name__)


def plus_days(count):
    _date = datetime.now()
    return _date + timedelta(days=count)


PLUS_ONE_MONTH = plus_days(count=31)
PLUS_ONE_YEAR = plus_days(count=366)


def create_or_update_user_profile(user, timestamp_or_date):
    #
    # timestamp_or_date can be instance of
    #  (1) datetime.date
    #  (2) timestamp e.g. 122343454 = expressed as integer
    #  (3) timestamp e.g. 232321133 = expressed as string
    #
    #  (2) and (3) input is received from stripe API
    #  (1) is used in testing, just to make sure it works as expected

    if isinstance(timestamp_or_date, int):
        some_date = date.fromtimestamp(timestamp_or_date)
    elif isinstance(timestamp_or_date, str):
        some_date = date.fromtimestamp(int(timestamp_or_date))
    else:
        some_date = timestamp_or_date

    # some_date instance of datetime.date

    if hasattr(user, 'profile'):
        logger.info(
            f"user already has a profile; some_date={some_date}"
        )
        user.profile.update_pro_enddate(some_date)
        user.save()
        logger.info(f"pro_enddate={user.profile.pro_enddate}")
        logger.info(f"is_pro={user.profile.is_pro_user()}")
    else:
        profile = UserProfile(
            user=user,
            pro_enddate=some_date
        )
        profile.save()


def upgrade_with_pro_url(lesson_order):
    base_url = reverse('upgrade')
    query_string = urlencode(
        {
            'lesson-order': lesson_order,
            'step': 2
        }
    )
    return f"{base_url}?{query_string}"


def upgrade_with_pro(lesson_order):
    url = upgrade_with_pro_url(lesson_order)

    return HttpResponseRedirect(url)


def login_with_pro(lesson_order):
    """
    Returns an HttpResponseRedirect to login window with
    two parameters lesson-order and step=1
    """
    base_url = reverse('account_login')
    query_string = urlencode(
        {
            'lesson-order': lesson_order,
            'step': 1
        }
    )
    url = f"{base_url}?{query_string}"

    return HttpResponseRedirect(url)


def paypal_with_params_url(automatic, lesson_plan_id):
    base_url = reverse('paypal_view')
    query_string = urlencode(
        {
            'plan': lesson_plan_id,
            'automatic': automatic
        }
    )
    url = f"{base_url}?{query_string}"

    return url
