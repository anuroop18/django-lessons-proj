from django.urls import path

from lessons import views

urlpatterns = [
    path('', views.index, name='index'),
]