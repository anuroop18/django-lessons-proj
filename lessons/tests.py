from datetime import date, datetime, timedelta

from django.test import Client, TestCase
from django.urls import reverse

from .models import Lesson, User
from .payments.stripe import create_or_update_user_profile
from .payments.utils import PLUS_ONE_MONTH, PLUS_ONE_YEAR


class UserProfileTest(TestCase):
    def setUp(self):
        self.user = User(username="user1")
        self.user.save()

    def test_user_model_has_profile(self):
        """
        User model has a signal associated which should create an user profile
        if user model is created.
        """
        self.assertTrue(
            hasattr(self.user, 'profile')
        )

        self.assertFalse(
            self.user.profile.is_pro_user()
        )

    def test_initial_user_with_temporary_discount(self):
        """
        Initial user (not PRO) with temporary discount will be able to
        watch PRO screencasts
        """
        # without discount user is not a PRO
        self.assertFalse(
            self.user.profile.is_pro_user()
        )
        today = date.today()
        _15_days = timedelta(days=15)
        # with discount create (15 days in future)
        self.user.profile.discount_enddate = today + _15_days
        self.user.profile.save()
        # user is now PRO (he didn't pay, he has a temporary discount)
        self.assertTrue(
            self.user.profile.is_pro_user()
        )

    def test_update_pro_enddate(self):
        today = date.today()
        days30 = timedelta(days=30)
        # date in future in future

        self.assertFalse(
            self.user.profile.is_pro_user()
        )

        self.user.profile.update_pro_enddate(
            some_date=today + days30
        )
        user = User.objects.get(id=self.user.id)
        self.assertTrue(
            user.profile.is_pro_user()
        )

    def test_create_or_update_user_profile(self):
        today = date.today()
        days30 = timedelta(days=30)

        self.assertFalse(
            self.user.profile.is_pro_user()
        )
        create_or_update_user_profile(
            self.user,
            today + days30
        )
        user = User.objects.get(id=self.user.id)
        self.assertTrue(
            user.profile.is_pro_user()
        )

    def test_create_or_update_user_profile_input_1(self):
        """
        create_or_update_user_profile gets an input an timestamp
        of a date in the future (as int)
        """
        now = datetime.now()
        days30 = timedelta(days=30)
        timestamp_in_future = int(
            datetime.timestamp(now + days30)
        )

        self.assertFalse(
            self.user.profile.is_pro_user()
        )
        create_or_update_user_profile(
            self.user,
            timestamp_in_future
        )
        user = User.objects.get(id=self.user.id)
        self.assertTrue(
            user.profile.is_pro_user()
        )

    def test_create_or_update_user_profile_input_2(self):
        """
        create_or_update_user_profile gets an input an timestamp
        of a date in the future (as str)
        """
        now = datetime.now()
        days30 = timedelta(days=30)
        timestamp_in_future = int(
            datetime.timestamp(now + days30)
        )
        timestamp_in_future = str(timestamp_in_future)

        self.assertFalse(
            self.user.profile.is_pro_user()
        )
        create_or_update_user_profile(
            self.user,
            timestamp_in_future
        )
        self.assertTrue(
            self.user.profile.is_pro_user()
        )

    def test_create_or_update_user_profile_plus_one_month(self):
        """
        use PLUS_ONE_MONTH constant to update
        user profile.
        """
        self.assertFalse(
            self.user.profile.is_pro_user()
        )
        create_or_update_user_profile(
            self.user,
            PLUS_ONE_MONTH
        )
        self.assertTrue(
            self.user.profile.is_pro_user()
        )

    def test_create_or_update_user_profile_plus_one_year(self):
        """
        use PLUS_ONE_YEAR constant to update user profile.
        """
        self.assertFalse(
            self.user.profile.is_pro_user()
        )
        create_or_update_user_profile(
            self.user,
            PLUS_ONE_YEAR
        )
        self.assertTrue(
            self.user.profile.is_pro_user()
        )


class LessonsOrderTests(TestCase):
    def test_initial_order(self):
        # if no other lesson is found in DB, initial
        # lesson order will be = 1
        self.assertEqual(
            1, Lesson.next_order()
        )


class PageViewTests(TestCase):

    def setUp(self):
        self.client = Client()

    def test_about(self):
        resp = self.client.get(reverse('about'))

        self.assertEqual(
            resp.status_code, 200
        )

    def test_privacy(self):
        resp = self.client.get(reverse('privacy'))

        self.assertEqual(
            resp.status_code, 200
        )

    def test_impressum(self):
        resp = self.client.get(reverse('impressum'))

        self.assertEqual(
            resp.status_code, 200
        )
