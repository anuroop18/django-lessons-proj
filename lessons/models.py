import datetime

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from modelcluster.contrib.taggit import ClusterTaggableManager
# tag related
from modelcluster.fields import ParentalKey
from taggit.models import Tag, TaggedItemBase
from wagtail.admin.edit_handlers import (FieldPanel, InlinePanel,
                                         StreamFieldPanel)
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Orderable, Page
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock

FREE = 'free'  # it is always better to use constants instead of strings
PRO = 'pro'


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    pro_enddate = models.DateField(
        null=True,
        blank=True
    )

    # In case user pays via Stripe and opts for
    # subcription all
    #  * stripe_subscription_id
    #  * stripe_customer_id
    #  * stripe_product_id
    # will be stored.
    # (this allows stripe's subscription cancelation)
    stripe_subscription_id = models.CharField(
        null=True,
        blank=True,
        max_length=64,
    )

    stripe_customer_id = models.CharField(
        null=True,
        blank=True,
        max_length=64,
    )

    stripe_product_id = models.CharField(
        null=True,
        blank=True,
        max_length=64,
    )

    # store one time paypal payment reference for this user
    paypal_order_id = models.CharField(
        max_length=64,
        blank=True,
        null=True
    )
    # store paypal subscription reference for this user
    paypal_subscription_id = models.CharField(
        max_length=64,
        blank=True,
        null=True
    )

    @property
    def is_with_automatic_renew(self):
        if not self.stripe_subscription_id:
            return False

        return True

    def update_pro_enddate(self, some_date):
        self.pro_enddate = some_date
        self.save()

    def is_pro_user(self):
        # If pro_enddate is not defined, blank or null
        # user is not a PRO
        if not self.pro_enddate:
            return False

        # if PRO is set in future(user paid for PRO account)
        # means he/she is a PRO
        if datetime.date.today() < self.pro_enddate:
            return True


class LessonsIndex(Page):
    """ Lessons index """
    pass


class NoteBlock(blocks.StructBlock):
    text = blocks.TextBlock()
    note_type = blocks.ChoiceBlock(
        choices=(
            ('info', 'Info'),
            ('warning', 'Warning'),
            ('danger', 'Danger'),
            ('note', 'Note'),
        ),
        required=False,
        default='info',
    )

    class Meta:
        template = 'lessons/blocks/note.html'


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
        lessons = Lesson.objects.filter(live=True).filter(
            tags__name=tag
        ).order_by('-last_published_at')

        # Update template context
        context = super().get_context(request)
        context['lessons'] = lessons
        context['tags'] = Tag.objects.order_by('name')
        context['current_tag_name'] = tag

        return context


class LessonTag(TaggedItemBase):
    content_object = ParentalKey(
        'Lesson',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )


class SimilarLesson(Orderable):
    # https://goonan.io/manytomany-relationships-in-wagtail/
    post = ParentalKey(
        'Lesson',
        related_name='similar_lessons'
    )
    page = models.ForeignKey(
        'Lesson',
        related_name="+",
        on_delete=models.CASCADE
    )
    panels = [
        FieldPanel('page')
    ]


class Lesson(Page):

    order = models.IntegerField(blank=True, default=0)

    short_description = RichTextField()

    lesson_type = models.CharField(
        choices=[(FREE, 'Free'), (PRO, 'Pro')],
        null=True,
        default='free',
        max_length=16,
    )

    image = models.ImageField(
        upload_to='uploads/',
        default='static/img/lesson.jpg'
    )

    tags = ClusterTaggableManager(
        through=LessonTag,
        blank=True
    )

    script = RichTextField(blank=True)

    # absolete: to be removed (replaced by similar_lessons)
    related_lessons = models.ManyToManyField(
        "self",
        blank=True,
        related_name='related_lessons',
    )

    content = StreamField([
        ('paragraph', blocks.RichTextBlock()),
        ('pro_paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('pro_image', ImageChooserBlock()),
        ('embed', EmbedBlock()),
        ('pro_embed', EmbedBlock()),
        ('code', CodeBlock()),
        ('pro_code', CodeBlock()),
        ('note', NoteBlock())
    ], blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('order'),
        FieldPanel('lesson_type'),
        FieldPanel('first_published_at'),
        FieldPanel('image'),
        FieldPanel('short_description'),
        FieldPanel('tags'),
        FieldPanel('script'),
        StreamFieldPanel('content'),
        # https://goonan.io/manytomany-relationships-in-wagtail/
        InlinePanel('similar_lessons', label="Similar Lessons")
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

    def get_next_lesson_obj(self):
        current_order = self.order
        ret = Lesson.objects.filter(live=True).filter(
            order=current_order + 1
        ).first()
        return ret

    def get_prev_lesson_obj(self):
        current_order = self.order
        ret = Lesson.objects.filter(live=True).filter(
            order=current_order - 1
        ).first()
        return ret

    def next_order():
        lessons = [
            obj.order for obj in Lesson.objects.all()
        ]

        if len(lessons) == 0:
            return 1

        return max(lessons) + 1


class Course(Page):
    short_description = RichTextField()
    image = models.ImageField(
        upload_to='uploads/',
        default='static/img/lesson.jpg'
    )

    lessons = models.ManyToManyField(Lesson, through='LessonGroup')

    content_panels = Page.content_panels + [
        FieldPanel('image'),
        FieldPanel('short_description'),
    ]

    def __str__(self):
        return self.title

    def get_context(self, request):

        lesson_groups = LessonGroup.objects.filter(
            course=self
        ).order_by('order')

        # Update template context
        context = super().get_context(request)
        context['lesson_groups'] = lesson_groups

        return context


class LessonGroup(models.Model):

    # within a course, title of the lesson will be different
    title = models.CharField(max_length=128, default='')
    short_description = RichTextField()
    order = models.IntegerField(blank=True, default=0)
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='lesson_groups'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='lesson_groups'
    )

    def get_next_lesson_group_obj(self):
        current_order = self.order
        ret = LessonGroup.objects.filter(
            order=current_order + 1
        ).first()
        return ret

    def get_prev_lesson_group_obj(self):
        current_order = self.order
        ret = LessonGroup.objects.filter(
            order=current_order - 1
        ).first()
        return ret

    def __str__(self):
        return self.title


class Subscription(models.Model):
    email = models.EmailField(blank=False)

    def __str__(self):
        return f"{self.email}"

    def __repr__(self):
        return f"{self.email}"


class Contact(models.Model):
    email = models.EmailField(blank=False)

    subject = models.CharField(
        max_length=256,
        blank=False
    )

    text = models.TextField(blank=False)

    def __str__(self):
        return f"{self.subject}"

    def __repr__(self):
        return f"{self.subject}"
