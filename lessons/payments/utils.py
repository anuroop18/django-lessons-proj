from django.shortcuts import HttpResponseRedirect
from django.urls import reverse
from django.utils.http import urlencode


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
