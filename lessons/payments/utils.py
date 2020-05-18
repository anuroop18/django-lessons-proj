from django.urls import reverse
from django.shortcuts import HttpResponseRedirect
from django.utils.http import urlencode


def upgrade_with_pro(lesson_order):
    base_url = reverse('upgrade')
    query_string = urlencode(
        {
            'lesson-order': lesson_order,
            'step': 2
        }
    )
    url = f"{base_url}?{query_string}"

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
