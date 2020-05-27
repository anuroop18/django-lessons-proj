from django.conf import settings


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

    def create_subscription(self, lesson_plan):
        response = PaymentResponse(
            self.client.create_subscription(lesson_plan)
        )
        return response

    def create_onetime_order(self, lesson_plan):
        response = PaymentResponse(
            self.client.create_onetime_order(lesson_plan)
        )
        return response
