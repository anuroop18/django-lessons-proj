from django.conf import settings
from stripe import (
    Customer,
    Subscription,
    PaymentIntent
)

MONTH = 'month'
YEAR = 'year'

API_KEY = settings.STRIPE_SECRET_KEY
PLAN_DICT = {
    MONTH: settings.STRIPE_PLAN_MONTHLY_ID,
    YEAR: settings.STRIPE_PLAN_ANNUAL_ID
}


class LessonsMonthPlan:
    def __init__(self):
        self.stripe_plan_id = settings.STRIPE_PLAN_MONTHLY_ID
        self.amount = 19.95
        self.currency = "usd"


class LessonsAnnualPlan:
    def __init__(self):
        self.stripe_plan_id = settings.STRIPE_PLAN_ANNUAL_ID
        self.amount = 199.50
        self.currency = "usd"


def create_payment_intent(
    payment_intent = PaymentIntent.create(
        api_key=API_KEY,
        amount=19.95,
        currency="usd",
        payment_method_types=["card"],
    )
):
    pass


def create_payment_subscription(
    email,
    plan_key  # = 'month' | 'year'
):


    customer = Customer.create(
        api_key=API_KEY,
        email=email,
    )

    subscription = Subscription.create(
        api_key=API_KEY,
        customer=customer.id,
        items=[
            {
                'plan': PLAN_DICT[plan_key],
            },
        ],
        expand=['latest_invoice.payment_intent'],
    )
    import pdb; pdb.set_trace()
    return subscription.status

    
