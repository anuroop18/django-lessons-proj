from django.urls import path

from lessons import views

urlpatterns = [
    path('', views.index, name='index'),
    path('/privacy', views.privacy, name='privacy'),
    path('/impressum', views.impressum, name='impressum'),
]
