from django.shortcuts import render
from lessons.models import Lesson


def index(request):
    lessons = Lesson.objects.all().order_by('-updated_at')

    return render(
        request,
        'lessons/index.html',
        {'lessons': lessons}
    )


def impressum(request):
    return render(request, 'lessons/impressum.html')


def privacy(request):
    return render(request, 'lessons/privacy.html')
