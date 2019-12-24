from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def nav_item_active(context):
    """
    Yet to be implemented
    """
    return ''
