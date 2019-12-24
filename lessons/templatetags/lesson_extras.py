from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def item_active_on(context, name):
    """
    Yet to be implemented
    """
    if context.get('active') == name:
        return 'active'

    return ''

