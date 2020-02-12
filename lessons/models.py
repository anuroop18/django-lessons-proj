from django.db import models
from django.urls import reverse

# tag related
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

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


class CodeBlock(blocks.StructBlock):
    code = blocks.TextBlock()
    lang = blocks.ChoiceBlock(
        choices=(
            ('python', 'Python'),
            ('bash', 'Bash'),
            ('javascript', 'Javascript'),
            ('json', 'JSON'),
            ('jinja', 'Django/jinja'),
        ),
        required=False,
        default='',
    )

    class Meta:
        template = 'lessons/blocks/code.html'
        icon = 'cup'


class LessonTagIndex(Page):
    def get_context(self, request):

        # Filter by tag
        tag = request.GET.get('tag')
        lessons = Lesson.objects.filter(tags__name=tag)

        # Update template context
        context = super().get_context(request)
        context['lessons'] = lessons
        context['tags'] = Lesson.tags.most_common()

        return context


class LessonTag(TaggedItemBase):
    content_object = ParentalKey(
        'Lesson',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )


class Lesson(Page):

    order = models.IntegerField(blank=True, default=0)

    short_description = RichTextField()

    image = models.ImageField(
        upload_to='uploads/',
        default='static/img/lesson.jpg'
    )

    tags = ClusterTaggableManager(
        through=LessonTag,
        blank=True
    )

    script = RichTextField(blank=True)

    content = StreamField([
        ('paragraph', blocks.RichTextBlock()),
        ('pro_paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('pro_image', ImageChooserBlock()),
        ('embed', EmbedBlock()),
        ('pro_embed', EmbedBlock()),
        ('code', CodeBlock()),
        ('pro_code', CodeBlock()),
    ], blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('order'),
        FieldPanel('first_published_at'),
        FieldPanel('image'),
        FieldPanel('short_description'),
        FieldPanel('tags'),
        FieldPanel('script'),
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


class Subscription(models.Model):
    email = models.EmailField(blank=False)

    def __str__(self):
        return f"{self.email}"

    def __repr__(self):
        return f"{self.email}"
