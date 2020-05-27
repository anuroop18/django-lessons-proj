from django.urls import path

from . import views
from .feed import LatestLessonsFeed
from .views import PageView
from .webhooks.paypal import webhook as paypal_webhook
from .webhooks.stripe import webhook as stripe_webhook

urlpatterns = [
    path('', views.index, name='index'),
    path(
        'lesson/lesson-<int:order>-<slug:slug>',
        views.lesson,
        name='lesson'
    ),
    path('subscribe', views.subscribe, name='subscribe'),
    path('contact', views.contact, name='contact'),
    path('upgrade', views.upgrade, name='upgrade'),
    path(
        'cancel-subsription',
        views.cancel_subscription,
        name='cancel_subscription'
    ),
    path(
        'paypal',
        views.paypal,
        name='paypal_view'
    ),
    path('checkout', views.checkout, name='checkout'),
    path('card', views.card, name='card'),
    path('thank-you', views.thank_you, name='thank_you'),
    path('stripe-webhooks', stripe_webhook, name='stripe_webhooks'),
    path('paypal-webhooks', paypal_webhook, name='paypal_webhooks'),
    path('profile', views.user_profile, name='user_profile'),
    path('latest/feed/', LatestLessonsFeed(), name='feed'),
    path('500', views.handler500, name='handler500'),
    path('sentry-debug/', views.trigger_error)
]

pages = [
    'privacy',
    'impressum',
    'about',
    'cookies',
    'services',
    'prices',
    'mission',
    'terms'
]

for page in pages:
    urlpatterns.append(
        path(
            page,
            PageView.as_view(template_name=f"lessons/{page}.html"),
            name=page
        ),
    )
