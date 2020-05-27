import logging

from django.conf import settings
from django.contrib.auth.models import User

from .clients.paypal import paypal_client
from .plans import ANNUAL_AS_STRING, MONTHLY_AS_STRING
from .utils import PLUS_ONE_MONTH, PLUS_ONE_YEAR, create_or_update_user_profile

SUBSCRIPTION = 'subscription'
ORDER = 'order'

logger = logging.getLogger(__name__)


def mode():
    if settings.DEBUG:
        return "sandbox"

    return "live"


def get_url_from(iterator, what):
    for link in iterator:
        if link['rel'] == what:
            return link['href']


class PaymentResponse:
    def __init__(self, paypal_ret):
        self._paypal_ret = paypal_ret

    @property
    def status(self):
        return self._paypal_ret['status']

    @property
    def id(self):
        return self._paypal_ret['id']

    def redirect_url(self, name):
        url = get_url_from(
            self._paypal_ret['links'], 'approve'
        )
        return url


class Payment:

    def __init__(
        self,
        client,
        user
    ):
        self._client = client
        self._user = user

    @property
    def client(self):
        return self._client

    @property
    def user(self):
        return self._user

    @property
    def profile(self):
        return self._user.profile

    def create_subscription(self, lesson_plan):
        """
        lesson_plan is an instance of lessons.plans.LessonsPlan
        """
        response = PaymentResponse(
            self.client.create_subscription(lesson_plan)
        )
        self.save_subscripion(
            subs_id=response.id
        )
        return response

    def create_onetime_order(self, lesson_plan):
        response = PaymentResponse(
            self.client.create_onetime_order(lesson_plan)
        )
        self.save_order(
            order_id=response.id
        )
        return response

    def save_subscripion(self, subs_id):
        self.profile.paypal_subscription_id = subs_id
        self.profile.save()

    def save_order(self, order_id):
        self.profile.paypal_order_id = order_id
        self.profile.save()


def set_paid_until_subscription(obj):
    billing_agreement_id = obj['billing_agreement_id']
    logger.info(
        f"Fetching billing_agreement_id={billing_agreement_id} details."
    )
    ret = paypal_client.get_subscription(
        billing_agreement_id
    )

    try:
        logger.info(
            f"Fetching associated user."
        )
        user = User.objects.get(profile__paypal_subscription_id=ret['id'])
    except User.DoesNotExist:
        logger.error(f"User with order id={ret['id']} not found.")
        return False

    logger.info(f"SUBSCRIPTION {obj} for user {user.email}")
    amount = obj['amount']['total']
    if amount == MONTHLY_AS_STRING:
        create_or_update_user_profile(user, PLUS_ONE_MONTH)
    elif amount == ANNUAL_AS_STRING:
        create_or_update_user_profile(user, PLUS_ONE_YEAR)
    else:
        logger.error(
            f"Paypal subscription with unexpected amount of {amount}"
        )

    return True


def set_paid_until_order(obj):
    url = get_url_from(obj['links'], 'self')
    ret = paypal_client.get_url(url)
    try:
        user = User.objects.get(profile__paypal_order_id=ret['id'])
    except User.DoesNotExist:
        logger.error(f"User with order id={ret['id']} not found.")
        return False

    logger.info(f"ORDER {obj} for user {user.email}")

    return True


def set_paid_until(obj, from_what):

    if from_what == SUBSCRIPTION:
        return set_paid_until_subscription(obj)

    if from_what == ORDER:
        return set_paid_until_order(obj)

    return True
