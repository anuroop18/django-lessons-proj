from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler500

urlpatterns = [
    path('', include('lessons.urls')),
    path('admin/', admin.site.urls),
]

handler500 = 'lessons.views.handler500'
