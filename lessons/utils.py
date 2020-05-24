from django.contrib.auth import get_user_model


def create_user(username, password):
    User = get_user_model()

    user = User.objects.create_user(
        username=username,
        is_active=True,
    )
    user.set_password(password)
    user.save()
    return user
