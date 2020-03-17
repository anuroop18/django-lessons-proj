from django.conf import settings
from stripe import (
    Customer,
    Subscription
)

API_KEY = settings.STRIPE_PUBLISHABLE_KEY
PLAN_DICT = {
    'month': settings.STRIPE_PLAN_MONTHTLY_ID,
    'annual': settings.STRIPE_PLAN_ANNUAL_ID
}


def create_payment_subscription(
    email,
    plan_key  # = 'month' | 'year'
):

    customer = Customer.create(
        api_key=API_KEY,
        email=email,
    )

    Subscription.create(
        api_key=API_KEY,
        customer=customer.id,
        items=[
            {
                'plan': PLAN_DICT[plan_key],
            },
        ],
        expand=['latest_invoice.payment_intent'],
    )
