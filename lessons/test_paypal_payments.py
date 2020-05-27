from django.test import TestCase

# my stripe = my own stripe module located in
# lessons.payments.stripe
from .payments import paypal as my_paypal
from .payments import plans
from .payments.clients.paypal import FakeClient as PaymentTestClient
from .utils import create_user


class UserProfileTest(TestCase):
    def setUp(self):
        self.user = create_user(
            username="test",
            password="test"
        )

    def test_basic(self):
        payment = my_paypal.Payment(
            client=PaymentTestClient("fake"),
            user=self.user,
        )
        plan = plans.LessonsPlan(
            plan_id=plans.ID_M,
            automatic='on'
        )
        payment.create_subscription(
            lesson_plan=plan
        )
