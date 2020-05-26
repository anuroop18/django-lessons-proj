import os

import paypalrestsdk
import yaml
from django.conf import settings
from lessons.payments import plans

BASE_DIR = os.path.join(
    "..",  # proj
    "..",  # land
    os.path.dirname(__file__)  # commands
)

ORDER_A_CONF_PATH = os.path.join("paypal", "order-annual.yml")
ORDER_M_CONF_PATH = os.path.join("paypal", "order-monthly.yml")


class BaseClient:
    """
    A thin wrapper over Paypal SDK.
    For unit tests will be replaced with own test client.
    """

    def __init__(self, mode):
        self._mode = mode
        self._api = None

    @property
    def api_key(self):
        return self._api_key

    def create_subscription(self, lesson_plan):
        pass

    def create_onetime_order(self, lesson_plan):
        pass


class RealClient(BaseClient):
    def __init__(self, mode):
        self._mode = mode
        self._api = paypalrestsdk.Api({
            "mode": mode,  # noqa
            "client_id": settings.PAYPAL_CLIENT_ID,
            "client_secret": settings.PAYPAL_CLIENT_SECRET
        })

    def create_subscription(self, lesson_plan):
        data = {
            'plan_id': lesson_plan.paypal_plan_id,
        }
        return self._api.post(
            "v1/billing/subscriptions",
            data
        )

    def get_order(self, lesson_plan):
        data = None

        if isinstance(lesson_plan.plan, plans.LessonsAnnualPlan):
            order_path = ORDER_A_CONF_PATH
        elif isinstance(lesson_plan.plan, plans.LessonsMonthPlan):
            order_path = ORDER_M_CONF_PATH
        else:
            raise ValueError("Unexpected lesson plan instance")

        with open(order_path, "r") as f:
            data = yaml.safe_load(f)

        return data

    def create_onetime_order(self, lesson_plan):
        order_dict = self.get_order(lesson_plan)

        return self._api.post(
            "v2/checkout/orders",
            order_dict
        )


class FakeClient(BaseClient):
    def __init__(self, mode):
        pass


def _mode():
    if settings.DEBUG:
        return "sandbox"

    return "live"


def get_paypal_client():
    if hasattr(settings, 'TEST') and settings.TEST is True:
        return FakeClient(mode='blah')

    return RealClient(
        mode=_mode()
    )


paypal_client = get_paypal_client()
