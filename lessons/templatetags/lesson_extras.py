from django import template
from django.utils.http import urlencode


register = template.Library()


@register.inclusion_tag("lessons/includes/userline.html")
def django_lessons_userline(user):

    accounts = {}
    userline_dict = {
        'username': user.username
    }

    for account in user.socialaccount_set.all().iterator():
        providers = accounts.setdefault(account.provider, [])
        providers.append(account)

    if accounts and accounts.get('github', False):
        github = accounts.get('github', False)
        if github and len(github) > 0:
            extra_data = github[0].extra_data

            if extra_data.get('login', False):
                userline_dict['username'] = github[0].extra_data['login']

            if extra_data.get('avatar_url', False):
                userline_dict['avatar_url'] = extra_data['avatar_url']

            userline_dict['provider'] = 'GitHub'

    if accounts and accounts.get('google', False):
        google = accounts.get('google', False)
        if google and len(google) > 0:
            extra_data = google[0].extra_data
            if extra_data.get('name', False):
                userline_dict['username'] = extra_data['name']

            if extra_data.get('picture', False):
                userline_dict['avatar_url'] = extra_data['picture']

            userline_dict['provider'] = 'Google'

    return userline_dict


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


@register.simple_tag(takes_context=True)
def activate_on(context, name, *names):
    """
    Used to activate/highlight current menu item.
    https://django-lessons.com/lesson/lesson-28-render-menu-one-active-item
    """
    if context['request'].resolver_match.url_name == name:
        return 'active'

    if context['request'].resolver_match.url_name in names:
        return 'active'

    return ''


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
