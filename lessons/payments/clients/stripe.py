from django.conf import settings
import stripe as orig_stripe


class Fake:
    @property
    def id(self):
        return "fake_id"

    @property
    def status(self):
        return "fake_status"


class FakeCustomer(Fake):
    pass


class FakeSubscription(Fake):
    pass


class FakePaymentIntent(Fake):
    pass


class BaseClient:
    """
    A thin wrapper over Stripe SDK.
    For unit tests will be replaced with own test client.
    """

    def __init__(self, api_key):
        self._api_key = api_key

    @property
    def api_key(self):
        return self._api_key

    def create_customer(
        self,
        email,
        payment_method_id,
        invoice_settings
    ):
        pass

    def retrieve_customer(self, customer_id):
        pass

    def create_subscription(self, customer, stripe_plan_id):
        pass

    def retrieve_subscription(self, subscription_id):
        pass

    def retrieve_payment_intent(self, payment_intent):
        pass

    def confirm_payment_intent(self, payment_intent):
        pass

    def cancel_subscription(self, subscription_id):
        pass


class RealClient(BaseClient):
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

    def create_customer(
        self,
        email,
        payment_method_id,
        invoice_settings
    ):
        customer = orig_stripe.Customer.create(
            email=email,
            payment_method=payment_method_id,
            invoice_settings=invoice_settings
        )
        return customer

    def retrieve_customer(self, customer_id):
        customer = orig_stripe.Customer.retrieve(
            customer_id
        )
        return customer

    def create_subscription(self, customer, stripe_plan_id):
        """
        customer = is orig_stripe.Customer instance
        """
        subscription = orig_stripe.Subscription.create(
            customer=customer.id,
            items=[
                {
                    'plan': stripe_plan_id
                },
            ],
            expand=['latest_invoice.payment_intent'],
        )
        return subscription

    def retrieve_subscription(self, subscription_id):
        sub = orig_stripe.Subscription.retrieve(
            subscription_id
        )

        return sub

    def retrieve_payment_intent(self, payment_intent):
        pi = orig_stripe.PaymentIntent.retrieve(
            payment_intent
        )
        return pi

    def confirm_payment_intent(self, payment_intent):
        orig_stripe.PaymentIntent.confirm(
            payment_intent
        )

    def cancel_subscription(self, subscription_id):
        orig_stripe.Subscription.delete(subscription_id)


class FakeClient(BaseClient):
    def __init__(self, api_key):
        self._api_key = api_key

    @property
    def api_key(self):
        return self._api_key

    def create_customer(
        self,
        email,
        payment_method_id,
        invoice_settings
    ):
        return FakeCustomer()

    def retrieve_customer(self, customer_id):
        return FakeCustomer()

    def create_subscription(self, customer, stripe_plan_id):
        return FakeSubscription()

    def retrieve_subscription(self, subscription_id):
        return FakeSubscription()

    def retrieve_payment_intent(self, payment_intent):
        return FakePaymentIntent()

    def confirm_payment_intent(self, payment_intent):
        pass

    def cancel_subscription(self, subscription_id):
        pass


def get_stripe_client():
    if hasattr(settings, 'TEST') and settings.TEST is True:
        return FakeClient(api_key='blah')

    return RealClient(api_key=settings.STRIPE_SECRET_KEY)


stripe_client = get_stripe_client()
