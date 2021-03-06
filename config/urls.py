from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler500
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from lessons import views as lessons_views

urlpatterns = [
    path('', include('lessons.urls')),
    path('cms/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),
    path('pages/', include(wagtail_urls)),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path("accoutns/login/", lessons_views.login_view, name="account_login"),
]

handler500 = 'lessons.views.handler500'
