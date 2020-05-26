from django.conf import settings


def mode():
    if settings.DEBUG:
        return "sandbox"

    return "live"


class Payment:

    def __init__(
        self,
        client,
        user
    ):
        self._cleint = client
        self._user = user

    def create_subscription(self, lesson_plan):
        ret = self.client.create_subscription(lesson_plan)

    def create_onetime_order(self, lesson_plan):
        ret = self.client.create_onetime_order(lesson_plan)
