from datetime import date, timedelta

from django.test import TestCase
from django.test import Client
from django.contrib.auth import get_user_model
from wagtail.core.models import Page
from django.urls import reverse

from lessons.models import (Lesson, PRO)
from lessons.payments import utils as pay_utils
from lessons.payments.stripe import create_or_update_user_profile


User = get_user_model()

JOHN = "john"
MARRY = "marry"
PASS = "test"


def create_user(username, password):
    user = User.objects.create_user(
        username=username,
        is_active=True,
    )
    user.set_password(password)
    user.save()
    return user


def create_pro_user(username, password):
    user = create_user(username, password)
    today = date.today()
    days30 = timedelta(days=30)
    create_or_update_user_profile(
        user,
        today + days30
    )
    return user

class TestBasicUpload(TestCase):

    def setUp(self):
        create_user(username=JOHN, password=PASS)
        create_pro_user(username=MARRY, password=PASS)
        self.client = Client()

    def test_pro_lesson_access_by_not_pro_user_view(self):
        """
        John is logged in user and he didn't pay for PRO account.
        If he tried to access a PRO lesson, he will be redirected
        to upgrade view.
        """
        self.client.login(
            username=JOHN,
            password=PASS
        )
        homepage = Page.objects.get(url_path='/home/')
        pro_lesson = Lesson(
            title="Hello world",
            slug='hello-world',
            content="hello",
            lesson_type=PRO,
            short_description="This is about hello and it is about world."
        )
        homepage.add_child(instance=pro_lesson)
        retrieved_lesson = Lesson.objects.get(id=pro_lesson.id)
        ret = self.client.get(
            reverse('lesson', args=[retrieved_lesson.order, 'hello-world'])
        )
        self.assertEquals(
            ret.status_code,
            302
        )
        self.assertEquals(
            ret.url,
            pay_utils.upgrade_with_pro_url(retrieved_lesson.order)
        )

    def test_pro_lesson_access_by_PRO_user_view(self):
        """
        John is logged in user and he didn't pay for PRO account.
        If he tried to access a PRO lesson, he will be redirected
        to upgrade view.
        """
        self.client.login(
            username=MARRY,
            password=PASS
        )
        homepage = Page.objects.get(url_path='/home/')
        pro_lesson = Lesson(
            title="Hello world",
            slug='hello-world',
            content="hello",
            lesson_type=PRO,
            short_description="This is about hello and it is about world."
        )
        homepage.add_child(instance=pro_lesson)
        retrieved_lesson = Lesson.objects.get(id=pro_lesson.id)
        ret = self.client.get(
            reverse('lesson', args=[retrieved_lesson.order, 'hello-world'])
        )
        self.assertEquals(
            ret.status_code,
            200
        )
