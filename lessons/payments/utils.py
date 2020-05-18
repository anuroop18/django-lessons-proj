from django.urls import reverse
from django.shortcuts import HttpResponseRedirect
from django.utils.http import urlencode


def profile_with_pro_url(lesson_order):
    base_url = reverse('user_profile')
    query_string = urlencode(
        {
            'lesson-order': lesson_order,
            'step': 1
        }
    )
    return f"{base_url}?{query_string}"


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
