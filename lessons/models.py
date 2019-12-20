from django.db import models
from taggit.managers import TaggableManager
from embed_video.fields import EmbedVideoField
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass


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

    # owener
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
    published = models.BooleanField(default=False)
    # publish_date
    publish_date = models.DateField()

    def __str__(self):
        return f"#{self.order} {self.title}"
