from django.utils import timezone
from django.test import TestCase
from django.test import Client
from django.urls import reverse

from taggit.models import Tag

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
            description="Very interesting information about Django 3.0",
            created_at=timezone.now(),
            updated_at=timezone.now(),
            publish_date=timezone.now(),
            published=True,
            user=self.user,
        )
        self.lesson_1.tags.add("django")
        self.lesson_2 = Lesson.objects.create(
            title="Lesson2 ",
            order=1,
            description="Very interesting information about python3.8",
            created_at=timezone.now(),
            updated_at=timezone.now(),
            publish_date=timezone.now(),
            published=True,
            user=self.user,
        )
        self.lesson_2.tags.add("python")

    def test_index(self):
        resp = self.client.get(reverse('index'))

        self.assertEqual(
            resp.status_code, 200
        )

        self.assertEqual(
            resp.context['lessons'].count(),
            2
        )

    def test_index_filter(self):
        tag = Tag.objects.get(name="django")

        resp = self.client.get(
            reverse('index'),
            {'tag_id': tag.id}
        )

        # only lesson tagged django is returned
        self.assertEqual(
            resp.status_code, 200
        )

        self.assertEqual(
            resp.context['lessons'].count(),
            1
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

