from django.test import TestCase
from django.test import Client
from django.contrib.auth import get_user_model
from wagtail.core.models import Page
from django.urls import reverse

from lessons.models import (Lesson, PRO)
from lessons.payments import utils as pay_utils


User = get_user_model()


class TestBasicUpload(TestCase):

    def setUp(self):
        user = User.objects.create_user(
            username='john',
            is_active=True,
        )
        user.set_password('test')
        user.save()
        self.client = Client()

    def test_pro_lesson_access_by_not_pro_user_view(self):
        """
        John is logged in user and he didn't pay for PRO account.
        If he tried to access a PRO lesson, he will be redirected
        to upgrade view.
        """
        self.client.login(
            username='john',
            password='test'
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
