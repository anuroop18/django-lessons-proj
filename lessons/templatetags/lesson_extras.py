from django import template
from django.utils.http import urlencode


register = template.Library()


@register.inclusion_tag("lessons/includes/tweet.html")
def tweet_tag(title, lesson_url):

    url = urlencode({
        'url': lesson_url,
        'text': title,
        'via': 'DjangoLessons',
    })

    return {
        'url': url
    }


@register.simple_tag
def note_css_class(note_type):
    """
    Django Lesson Note Type

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

    mapped to bootstrap

    alert types css classes:
        https://getbootstrap.com/docs/4.3/components/alerts/
    """
    css_class_map = {
        'info': 'success',
        'warning': 'warning',
        'danger': 'danger',
        'note': 'primary'
    }

    return css_class_map.get(note_type, 'info')
