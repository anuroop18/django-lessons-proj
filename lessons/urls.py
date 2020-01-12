from django.urls import path

from lessons.feed import LatestLessonsFeed
from lessons import views
from lessons.views import PageView

urlpatterns = [
    path('', views.index, name='index'),
    path(
        'lesson/lesson-<int:order>-<slug:slug>',
        views.lesson,
        name='lesson'
    ),
    path(
        'subscribe',
        views.subscribe,
        name='subscribe'
    ),
    path('latest/feed/', LatestLessonsFeed(), name='feed'),
    path('500', views.handler500, name='handler500')
]

pages = [
    'privacy',
    'impressum',
    'about',
    'cookies',
]

for page in pages:
    urlpatterns.append(
        path(
            page,
            PageView.as_view(template_name=f"lessons/{page}.html"),
            name=page
        ),
    )
