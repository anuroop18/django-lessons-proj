from django.db import models
from django.urls import reverse
from taggit.managers import TaggableManager
from embed_video.fields import EmbedVideoField
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass


class LessonQuerySet(models.QuerySet):

    def published(self):
        return self.filter(public=True).order_by('-created_at')

    def tagged(self, tag_id=None):
        if tag_id:
            return self.filter(tags__id__in=[tag_id])

        return self.all()

    def search(self, title):
        if title:
            return self.filter(title__icontains=title)

        return self.all()


class LessonsManager(models.Manager):
    def get_queryset(self):
        return LessonQuerySet(self.model, using=self._db)

    def published(self):
        return self.get_queryset().published()

    def tagged(self, tag_id=None):
        return self.get_queryset().tagged(tag_id)

    def search(self, title):
        return self.get_queryset().search(title)


class Lesson(models.Model):

    # Lesson #5 (in this case field holds an integer value of 5)
    order = models.IntegerField(blank=True)

    # e.g. Starting a New Django Project - Right Way
    title = models.CharField(
        max_length=200,
        blank=False,
    )

    slug = models.SlugField(null=True)

    # a longer description
    description = models.TextField()

    # urls to further reading
    references = models.TextField(null=True, blank=True)

    image = models.ImageField(
        upload_to='uploads/',
        default='static/img/lesson.jpg'
    )
    video = EmbedVideoField(
        max_length=600,
        blank=True,
    )

    # owner
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
    )

    # free or pro lesson
    lesson_type = models.CharField(
        max_length=16,
        choices=[
            # free for everybody
            ('free', 'Free Lesson'),
            # for paid accounts
            ('pro', 'Pro Lesson'),
        ],
        default='free'
    )

    # will be automatically updated only during creation
    created_at = models.DateTimeField(auto_now_add=True)
    # will be automatically updated by django on every save
    updated_at = models.DateTimeField(auto_now=True)
    public = models.BooleanField(default=False)
    # publish_date
    publish_date = models.DateField()

    # managers
    objects = models.Manager()
    obj = LessonsManager()
    tags = TaggableManager()

    def __str__(self):
        return f"#{self.order} {self.title}"

    def get_absolute_url(self):
            return reverse(
                'lesson', kwargs={
                    'order': self.order,
                    'slug': self.slug
                }
            )

    def next_order():
        lessons = [
            obj.order for obj in Lesson.objects.all()
        ]

        if len(lessons) == 0:
            return 1

        return max(lessons) + 1


class Subscribtion(models.Model):
    email = models.EmailField(blank=False)

    def __str__(self):
        return f"{self.email}"

    def __repr__(self):
        return f"{self.email}"
