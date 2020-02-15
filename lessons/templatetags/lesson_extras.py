from django import template

register = template.Library()


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
