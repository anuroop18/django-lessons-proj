from django.db import models
from taggit.managers import TaggableManager
from embed_video.fields import EmbedVideoField
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass


class LessonQuerySet(models.QuerySet):

    def published(self):
        return self.filter(public=True)

    def ordered(self):
        return self.order_by('-updated_at')


class PublishedLessons(models.Manager):
    def get_queryset(self):
        return LessonQuerySet(self.model, using=self._db)


class Lesson(models.Model):

    # Lesson #5 (in this case field holds an integer value of 5)
    order = models.IntegerField()

    # e.g. Starting a New Django Project - Right Way
    title = models.CharField(
        max_length=200,
        blank=False,
        null=False
    )

    # a longer description
    description = models.TextField()

    image = models.ImageField(
        upload_to='uploads/',
        default='static/img/lesson.jpg'
    )
    video = EmbedVideoField(
        max_length=600,
        blank=True,
        null=True
    )

    # owner
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
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

    tags = TaggableManager()

    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    public = models.BooleanField(default=False)
    # publish_date
    publish_date = models.DateField()

    # managers
    objects = models.Manager()
    published = PublishedLessons()

    def __str__(self):
        return f"#{self.order} {self.title}"
