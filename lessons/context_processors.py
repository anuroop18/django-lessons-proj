from .models import Course


def courses(request):
    all_courses = Course.objects.order_by(
        '-first_published_at'
    )

    return {
        'courses': all_courses,
    }
