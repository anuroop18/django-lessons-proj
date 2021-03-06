from django.test import TestCase

# my stripe = my own stripe module located in
# lessons.payments.stripe
from .payments import stripe as my_stripe
from .payments.clients.stripe import FakeClient as PaymentTestClient
from .utils import create_user


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

    def test_payment_status_initial_state(self):
        status = my_stripe.PaymentStatus()
        self.assertIn(
            "not initiated", status.message
        )
        self.assertEquals(
            status.code, my_stripe.PaymentStatus.NOT_INITIATED
        )

    def test_status(self):
        status = my_stripe.PaymentStatus()
        status.set_status(
            my_stripe.PaymentStatus.SUCCESS
        )
        self.assertIn(
            "Thank You!", status.message
        )

    def test_status_equality(self):
        status = my_stripe.PaymentStatus()
        status.set_status(
            my_stripe.PaymentStatus.REQUIRES_ACTION
        )
        # status instance can be compares with status code
        self.assertTrue(
            status == my_stripe.PaymentStatus.REQUIRES_ACTION
        )

    def test_cancel_subsription(self):
        subs = my_stripe.Subscription(
            client=PaymentTestClient("fake"),
            user=self.user,)
        subs.cancel(
            subscription_id="whatever"
        )
        self.assertIn(
            "canceled", subs.status.message
        )

    def test_one_time_payment_basic(self):
        payment = my_stripe.OneTimePayment(
            client=PaymentTestClient("fake"),
            user=self.user,
            payment_method_id="blah",
            lesson_plan_id='m'  # LessonsPlan, monthly
        )
        payment.pay()
