from django.test import TestCase
from django.test import Client
from django.urls import reverse


class LessonsViewTests(TestCase):

    def setUp(self):
        self.client = Client()

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

