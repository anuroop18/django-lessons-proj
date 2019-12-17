from django.utils import timezone
from django.test import TestCase
from django.test import Client
from django.urls import reverse


from lessons.models import (Lesson, User)


class LessonsViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username="user1",
        )
        self.client = Client()
        self.lesson_1 = Lesson.objects.create(
            title="Lesson1 ",
            order=1,
            description="Very interesting information about python3.6",
            created_at=timezone.now(),
            updated_at=timezone.now(),
            publish_date=timezone.now(),
            published=True,
            user=self.user
        )

    def test_index(self):
        resp = self.client.get(reverse('index'))

        self.assertEqual(
            resp.status_code, 200
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

