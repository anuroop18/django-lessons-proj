from datetime import date, datetime, timedelta

from django.utils import timezone
from django.test import TestCase
from django.test import Client
from django.urls import reverse

from taggit.models import Tag

from lessons.models import (Lesson, User, UserProfile)
from lessons.payments import create_or_update_user_profile


class UserProfileTest(TestCase):
    def setUp(self):
        self.user = User(
            email="user1@mail.com",
            username="user1",
            password="abcxyz123"
        )
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

        self.assertTrue(
            self.user.profile.is_pro_user()
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
        self.assertTrue(
            self.user.profile.is_pro_user()
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
        self.assertTrue(
            self.user.profile.is_pro_user()
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

