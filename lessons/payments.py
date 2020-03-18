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
        self.amount = 1995
        self.currency = "usd"


class LessonsAnnualPlan:
    def __init__(self):
        self.stripe_plan_id = settings.STRIPE_PLAN_ANNUAL_ID
        self.amount = 19950
        self.currency = "usd"


def create_payment_intent(
    lesson_plan,
    payment_method_type="card"
):
    payment_intent = PaymentIntent.create(
        api_key=API_KEY,
        amount=lesson_plan.amount,
        currency=lesson_plan.currency,
        payment_method_types=[payment_method_type],
    )
    return payment_intent.client_secret


def create_payment_subscription(
    email,
    lesson_plan,  # = 'month' | 'year'
    payment_method_id
):
    customer = Customer.create(
        api_key=API_KEY,
        email=email,
        payment_method=payment_method_id,
        invoice_settings={
            'default_payment_method': payment_method_id,
        },
    )

    subscription = Subscription.create(
        api_key=API_KEY,
        customer=customer.id,
        items=[
            {
                'plan': lesson_plan.stripe_plan_id,
            },
        ],
    )
    return subscription.status


def upgrade_customer(invoice):
    """
    invoice = is stripe.invoice object instance
    from invoice.payment_succeeded webhook
    """
    # invoice['customer_email']
    # invoice['paid'] = true|false
    # invoice['subscription'] # hier is an id
    subscr = Subscription.retrieve(invoice['subscription'])
    subscr['current_period_start']
    subscr['current_period_end']
