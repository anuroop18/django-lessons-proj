import paypalrestsdk
from django.conf import settings
from lessons.payments import plans


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

    def create_onetime_order(self, lesson_plan):
        pass


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
