from django.urls import path

from lessons import views
from lessons.views import PageView
from django.conf.urls import handler500

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
    path('500', views.handler500, name='handler500')
]

handler500 = views.handler500

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
