from django.db import models
from django.urls import reverse

from wagtail.core.fields import RichTextField
from wagtail.core.models import Page
from wagtail.core import blocks
from wagtail.core.fields import StreamField
from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.admin.edit_handlers import FieldPanel


class LessonsIndex(Page):
    """ Lessons index """
    pass


class Lesson(Page):

    order = models.IntegerField(blank=True, default=0)

    short_description = RichTextField()

    content = StreamField([
        ('paragraph', blocks.RichTextBlock()),
        ('pro_paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('pro_image', ImageChooserBlock()),
        ('embed', EmbedBlock()),
        ('pro_embed', EmbedBlock()),
    ], blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('short_description'),
        FieldPanel('order'),
        StreamFieldPanel('content'),
    ]

    def __str__(self):
        return f"#{self.order} {self.title}"

    def save(self, *args, **kwargs):
        if not self.order:
            self.order = Lesson.next_order()

        super().save(*args, **kwargs)  # Call the "real" save() method.

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
