import logging

# Stripe SDK original module
import stripe as orig_stripe
from django.conf import settings
from django.contrib.auth.models import User
from lessons.payments import plans

from .plans import ANNUAL_AMOUNT, MONTHLY_AMOUNT
from .utils import PLUS_ONE_MONTH, PLUS_ONE_YEAR, create_or_update_user_profile

API_KEY = settings.STRIPE_SECRET_KEY
PLAN_DICT = {
    plans.MONTH: settings.STRIPE_PLAN_MONTHLY_ID,
    plans.YEAR: settings.STRIPE_PLAN_ANNUAL_ID
}

logger = logging.getLogger(__name__)

SUBSCRIPTION_ACTIVE = 'active'
SUBSCRIPTION_INACTIVE = 'inactive'
SUBSCRIPTION_INCOMPLETE = 'incomplete'
PAYMENT_SUCCEEDED = 'succeeded'


class PaymentStatus:

    # codes
    REQUIRES_ACTION = 'requires_action'
    NOT_INITIATED = 'not_initiated'
    SUCCESS = 'success'
    SUBSCRIPTION_CANCELED_SUCCESS = 'subscription_canceled_success'

    MESSAGES = {
        REQUIRES_ACTION: 'Requires action (3D secure user auth)',
        NOT_INITIATED: 'Payment process not initiated yet',
        SUCCESS: """Success! Thank You!
        It may take 2-3 minutes to process the payment and upgrade your account.
        """,
        SUBSCRIPTION_CANCELED_SUCCESS: """
        Subscription canceled :( Thank you for using Django Lessons!
        """
    }

    TAGS = {
        REQUIRES_ACTION: 'text-warning',
        NOT_INITIATED: 'text-success',
        SUCCESS: 'text-success',
        SUBSCRIPTION_CANCELED_SUCCESS: 'text-success'
    }

    TITLES = {
        REQUIRES_ACTION: 'Requires Action',
        NOT_INITIATED: 'Payment Not Yet Started',
        SUCCESS: 'Payment Success',
        SUBSCRIPTION_CANCELED_SUCCESS: 'Subscription Canceled'
    }

    def __init__(self):
        self._code = PaymentStatus.NOT_INITIATED

    @property
    def code(self):
        return self._code

    @property
    def message(self):
        return PaymentStatus.MESSAGES[self.code]

    @property
    def title(self):
        return PaymentStatus.TITLES[self.code]

    @property
    def tag(self):
        return PaymentStatus.TAGS[self.code]

    def set_status(self, code):
        self._code = code

    def __eq__(self, other_code):
        return self.code == other_code

    def __str__(self):
        return f"PaymentStatus(code={self.code}, message={self.message})"

    def __repr__(self):
        return str(self)


class Payment:
    def __init__(self, client, user):
        self._client = client
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

    @property
    def requires_action(self):
        return self.status == PaymentStatus.REQUIRES_ACTION


class OneTimePayment(Payment):

    def __init__(
        self,
        client,
        user,
        payment_method_id,
        lesson_plan_id
    ):
        super().__init__(
            client=client,
            user=user
        )
        self._payment_method_id = payment_method_id
        self._lesson_plan_id = lesson_plan_id

    @property
    def payment_method_id(self):
        return self._payment_method_id

    @property
    def lesson_plan_id(self):
        return self._lesson_plan_id

    def pay(self):
        lesson_plan = plans.LessonsPlan(
            plan_id=self.lesson_plan_id
        )
        payment_intent = self.client.create_payment_intent(
            amount=lesson_plan.amount,
            currency=lesson_plan.currency,
            receipt_email=self.user.email,
            payment_method_types=['card']
        )
        self.client.modify_payment_intent(
            payment_intent.id,
            payment_method_id=self.payment_method_id
        )
        ret = self.client.confirm_payment_intent(
            payment_intent.id
        )

        if ret.status == PAYMENT_SUCCEEDED:
            self.status.set_status(
                PaymentStatus.SUCCESS
            )
            return payment_intent

        if ret.status == PaymentStatus.REQUIRES_ACTION:
            self.status.set_status(
                PaymentStatus.REQUIRES_ACTION
            )
            return payment_intent

        return False

    def get_3ds_context(self, payment_intent_id):
        pi = self.client.retrieve_payment_intent(
            payment_intent=payment_intent_id
        )
        context = {}
        context['payment_intent_secret'] = pi.client_secret
        context['STRIPE_PUBLISHABLE_KEY'] = settings.STRIPE_PUBLISHABLE_KEY

        return context


class RecurringPayment(Payment):
    def __init__(
        self,
        client,
        user,
        payment_method_id,
        stripe_plan_id

    ):
        super().__init__(
            client=client,
            user=user
        )
        self._payment_method_id = payment_method_id
        self._stripe_plan_id = stripe_plan_id

    @property
    def payment_method_id(self):
        return self._payment_method_id

    @property
    def stripe_plan_id(self):
        return self._stripe_plan_id

    @property
    def customer_id(self):
        return self.user.profile.stripe_customer_id

    @property
    def subscription_id(self):
        return self.user.profile.stripe_subscription_id

    def get_3ds_context(self, latest_invoice):
        pi = self.client.retrieve_payment_intent(
            payment_intent=latest_invoice.payment_intent
        )
        context = {}
        context['payment_intent_secret'] = pi.client_secret
        context['STRIPE_PUBLISHABLE_KEY'] = settings.STRIPE_PUBLISHABLE_KEY

        return context

    def create_subscription(self):
        """
        In case of success (even if payment still requires action)
        will return orig_stripe.Invoice instance - which is latest invoice.
        In case of 3D secure, from latest invoice instance, the
        confirmation view is generated.
        In case of failure returns False.
        """
        customer = self.get_or_create_customer()

        subscription = self.get_or_create_subscription(
            customer,
            self.stripe_plan_id
        )

        # This subscription.status describes the status of
        # the payment intent for the latest subscription invoice.
        # The invoice tracks overall payment status for the
        # subscription; the payment intent tracks the status
        # of an individual payment.
        # To get this value, you must expand the child objects of the reponse.
        if subscription.status == SUBSCRIPTION_ACTIVE:
            self.status.set_status(
                PaymentStatus.SUCCESS
            )
            return subscription.latest_invoice

        if subscription.status == SUBSCRIPTION_INCOMPLETE:
            latest_inv = self.client.retrieve_invoice(
                subscription.latest_invoice
            )

            ret = self.client.confirm_payment_intent(
                payment_intent=latest_inv.payment_intent
            )
            if ret.status == PaymentStatus.REQUIRES_ACTION:
                self.status.set_status(
                    PaymentStatus.REQUIRES_ACTION
                )
                return latest_inv

        return False

    def get_or_create_subscription(self, customer, stripe_plan_id):
        """
        customer is orig_stripe.Customer instance.
        """
        if not self.subscription_id:
            sub = self.client.create_subscription(
                customer,
                stripe_plan_id
            )
            self.save_subscription_id(sub.id)
        else:
            sub = self.client.retrieve_subscription(
                self.subscription_id
            )

        return sub

    def get_or_create_customer(self):

        if not self.customer_id:
            customer = self.client.create_customer(
                email=self.user.email,
                payment_method_id=self.payment_method_id,
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
        self.user.profile.stripe_subscription_id = subscription_id
        self.user.profile.save()

    def save_customer_id(self, customer_id):
        self.user.profile.stripe_customer_id = customer_id
        self.user.profile.save()


class Subscription(Payment):
    def __init__(self, client, user):
        super().__init__(
            client=client,
            user=user
        )

    def cancel(self, subscription_id):
        self.client.cancel_subscription(subscription_id)

        self.user.profile.stripe_subscription_id = None
        self.user.profile.stripe_product_id = None
        self.user.profile.save()

        self.status.set_status(
            PaymentStatus.SUBSCRIPTION_CANCELED_SUCCESS
        )


def create_payment_intent(
    lesson_plan,
    payment_method_type="card"
):
    payment_intent = orig_stripe.PaymentIntent.create(
        api_key=API_KEY,
        amount=lesson_plan.amount,
        currency=lesson_plan.currency,
        payment_method_types=[payment_method_type],
    )
    return payment_intent


def upgrade_customer_from_charge(charge):
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
        current_period_end = PLUS_ONE_MONTH
    elif charge.amount == ANNUAL_AMOUNT:
        current_period_end = PLUS_ONE_YEAR
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

    subscr = orig_stripe.Subscription.retrieve(
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
