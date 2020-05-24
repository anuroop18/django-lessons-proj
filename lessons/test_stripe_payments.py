from django.test import TestCase

# my stripe = my own stripe module located in
# lessons.payments.stripe
from lessons.payments import stripe as my_stripe
from lessons.payments.clients.stripe import FakeClient as PaymentTestClient
from lessons.utils import create_user


class UserProfileTest(TestCase):
    def setUp(self):
        self.user = create_user(
            username="test",
            password="test"
        )

    def test_basic(self):
        payment = my_stripe.RecurringPayment(
            client=PaymentTestClient("fake"),
            user=self.user,
            stripe_plan_id='whatever_id',
            payment_method_id='whatever_id'
        )
        payment.create_subscription()

    def test_status(self):
        status = my_stripe.PaymentStatus()
        status.set_status(
            my_stripe.PaymentStatus.SUCCESS
        )
        self.assertIn(
            "Thank You!", status.message
        )
