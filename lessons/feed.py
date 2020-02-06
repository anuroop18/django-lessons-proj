from django.contrib.syndication.views import Feed
from lessons.models import Lesson


class LatestLessonsFeed(Feed):
    title = "Django Lessons"
    link = "/latest/"
    description = "Keep track of latest Lessons."

    def items(self):
        return Lesson.objects.order_by('-first_published_at')[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.short_description
