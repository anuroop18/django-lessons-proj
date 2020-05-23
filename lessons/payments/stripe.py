from datetime import date, timedelta
import logging
# Stripe SDK original module
import stripe as orig_stripe

from django.conf import settings
from django.contrib.auth.models import User
from stripe import (
    Subscription,
    PaymentIntent
)

from lessons.models import UserProfile

MONTH = 'month'
YEAR = 'year'
STATUS_PAID = 'paid'
MONTHLY_AMOUNT = 1995
ANNUAL_AMOUNT = 19950

API_KEY = settings.STRIPE_SECRET_KEY
PLAN_DICT = {
    MONTH: settings.STRIPE_PLAN_MONTHLY_ID,
    YEAR: settings.STRIPE_PLAN_ANNUAL_ID
}

logger = logging.getLogger(__name__)

SUBSCRIPTION_ACTIVE = 'active'
SUBSCRIPTION_INCOMPLETE = 'incomplete'


class PaymentStatus:

    # codes
    REQUIRES_ACTION = 'requires_action'

    def __init__(self):
        self._code
        self._message
        self._tag
        self._title

    def set_status(self, code):
        self._code = code

    def __eq__(self, other_code):
        return self.code == other_code


class PaymentClient:
    """
    A thin wrapper over Stripe SDK.
    For unit tests will be replaced with own test client.
    """

    def __init__(self, api_key):
        self._api_key = api_key
        orig_stripe.api_key = self._api_key

    @property
    def api_key(self):
        return self._api_key

    def create_customer(self, email, payment_method_id):
        customer = orig_stripe.Customer.create(
            email=email,
            payment_method=payment_method_id,
            invoice_settings={
                'default_payment_method': payment_method_id
            }
        )
        return customer

    def retrieve_customer(self, customer_id):
        customer = orig_stripe.Customer.retrieve(
            stripe_customer_id
        )
        return customer

    def create_subscription(self, customer, stripe_plan_id):
        """
        customer = is orig_stripe.Customer instance
        """
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[
                {
                    'plan': stripe_plan_id
                },
            ],
            expand=['latest_invoice.payment_intent'],
        )
        return subscription

    def retrieve_payment_intent(self, payment_intent):
        pi = orig_stripe.PaymentIntent.retrieve(
            payment_intent
        )
        return pi

    def confirm_payment_intent(self, payment_intent):
        orig_stripe.PaymentIntent.confirm(
            payment_intent
        )


class Payment:
    def __init__(self, api_key, user):
        self._client = PaymentClient(api_key=api_key)
        self._user = user
        self._status = PaymentStatus()

    @property
    def client(self):
        return self._client

    @property
    def user(self):
        return self._user

    @property
    def profile(self):
        return self._user.profile

    @property
    def status(self):
        return self._status


class OneTimePayment(Payment):

    def __init__(self):
        self._api_key = api_key


class RecurringPayment(Payment):
    def __init__(
        self,
        api_key,
        user,
        payment_method_id,
        stripe_plan_id

    ):
        super().__init__(
            api_key=api_key,
            user=user
        )
        self._payment_method_id = payment_method_id
        self._stripe_plan_id = stripe_plan_id
        self._latest_invoice = None

    @property
    def customer_id(self):
        return self.user.profile.stripe_customer_id

    @property
    def subscription_id(self):
        return self.user.profile.stripe_subscription_id

    @property
    def requires_action(self):
        return self.status == PaymentStatus.REQUIRES_ACTION

    @property
    def get_3ds_context(self):
        pi = self.client.retrieve_payment_intent(
            payment_intent=self._latest_invoice.payment_intent
        )
        context = {}
        context['payment_intent_secret'] = pi.client_secret
        context['STRIPE_PUBLISHABLE_KEY'] = settings.STRIPE_PUBLISHABLE_KEY

        return context

    def create_subscription(self):
        customer = self.get_or_create_customer()

        subscription = self.get_or_create_subscription(
            customer
        )

        if subscription.status == SUBSCRIPTION_ACTIVE:
            self.status.set_success()
            return True

        if subscription.status == SUBSCRIPTION_INACTIVE:
            latest_inv = self.client.retrieve_invoice(
                s.latest_invoice
            )

            ret = self.client.confirm_payment_intent(
                payment_intent=s.latest_invoice.payment_intent
            )
            if ret.status == PaymentStatus.REQUIRES_ACTION:
                self.status.set_status(
                    PaymentStatus.REQUIRES_ACTION
                )
                return True

        return True

    def get_or_create_subscription(self, customer):
        """
        customer is orig_stripe.Customer instance.
        """
        if not self.subscription_id:
            subscription = self.client.create_subscription(
                customer
            )
            self.save_subscription_id(subscription.id)
        else:
            subscription = stripe.Subscription.retrieve(
                user.profile.stripe_subscription_id
            )

        return subscription

    def get_or_create_customer(self):

        if not self.stripe_customer_id:
            customer = self.client.create_customer(
                email=self.user.email,
                payment_method=self.payment_method_id,
                invoice_settings={
                    'default_payment_method': self.payment_method_id
                }
            )
            self.save_customer_id(customer.id)
        else:
            customer = self.client.retrieve_customer(
                customer_id=self.customer_id
            )

        return customer

    def save_subscription_id(self, subscription_id):
        self.user.profile.stripe_subscription_id = subscription.id
        self.user.profile.save()


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


class LessonsMonthPlan:
    def __init__(self):
        self.stripe_plan_id = settings.STRIPE_PLAN_MONTHLY_ID
        self.amount = MONTHLY_AMOUNT


class LessonsAnnualPlan:
    def __init__(self):
        self.stripe_plan_id = settings.STRIPE_PLAN_ANNUAL_ID
        self.amount = ANNUAL_AMOUNT


class LessonsPlan:
    def __init__(self, plan_id, automatic=False):
        """
        plan_id is either string 'm' (stands for monthly)
        or a string letter 'a' (which stands for annual)
        """
        if plan_id == 'm':
            self.plan = LessonsMonthPlan()
            self.id = 'm'
        elif plan_id == 'a':
            self.plan = LessonsAnnualPlan()
            self.id = 'a'
        else:
            raise ValueError('Invalid plan_id value')

        self.currency = 'usd'
        self.automatic = automatic

    @property
    def stripe_plan_id(self):
        return self.plan.stripe_plan_id

    @property
    def amount(self):
        return self.plan.amount

    @property
    def human_details(self):
        msg = "PRO account "

        if self.automatic in ('True', 'on'):
            if isinstance(self.plan, LessonsMonthPlan):
                msg += "with monthly subscription."
            elif isinstance(self.plan, LessonsAnnualPlan):
                msg += "with annual subscription."
        else:
            if isinstance(self.plan, LessonsMonthPlan):
                msg += " for a month."
            elif isinstance(self.plan, LessonsAnnualPlan):
                msg += " for a year."
            msg += " No subscription."

        return msg

    @property
    def human_message(self):
        dollars = self.plan.amount / 100
        return f"${dollars:.2f}"


def get_or_create_customer(user, payment_method_id):



def get_or_create_subscription(
    user,
    customer,
    stripe_plan_id
):



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
    return payment_intent


def upgrade_customer_from_charge(charge):
    current_date = date.today()
    email = charge.receipt_email

    logger.info(f"email={email}")

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        logger.warning(
            f"User with email {email} not found while trying to upgrade to PRO"
        )
        return False

    if charge.amount == MONTHLY_AMOUNT:
        current_period_end = current_date + timedelta(days=31)
    elif charge.amount == ANNUAL_AMOUNT:
        current_period_end = current_date + timedelta(days=365)
    else:
        logger.error(
            "Unrecognizable amount received"
        )

    create_or_update_user_profile(user, current_period_end)


def upgrade_customer_from_invoice(invoice):
    """
    invoice = is stripe.invoice object instance
    from invoice.payment_succeeded webhook
    """
    # invoice['customer_email']
    # invoice['paid'] = true|false
    # invoice['current_period_end'] # timestamp of end of subscription
    email = invoice['customer_email']
    logger.info(f"email={email}")
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        logger.warning(
            f"User with email {email} not found while trying to upgrade to PRO"
        )
        return False

    subscr = Subscription.retrieve(
        api_key=API_KEY,
        id=invoice['subscription']
    )

    current_period_end = subscr['current_period_end']
    logger.info(f"subscription_id={invoice['subscription']}")
    logger.info(f"invoice paid = {invoice['paid']}")
    logger.info(f"pro_enddate= {subscr['current_period_end']}")

    if invoice['paid']:
        create_or_update_user_profile(user, current_period_end)
        logger.info(
            f"Profile with {current_period_end} saved for user {email}"
        )
    else:
        logger.info("Invoice is was NOT paid!")

    return True
