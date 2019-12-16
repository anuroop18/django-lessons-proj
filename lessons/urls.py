from django.urls import path

from lessons import views
from lessons.views import PageView

urlpatterns = [
    path('', views.index, name='index'),
]

pages = [
    'privacy',
    'impressum',
    'about'
]

for page in pages:
    urlpatterns.append(
        path(
            page,
            PageView.as_view(template_name=f"lessons/{page}.html"),
            name=page
        ),
    )
