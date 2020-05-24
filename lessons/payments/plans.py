from django.conf import settings

MONTH = 'month'
YEAR = 'year'
STATUS_PAID = 'paid'
MONTHLY_AMOUNT = 1995
ANNUAL_AMOUNT = 19950


class LessonsMonthPlan:
    def __init__(self):
        self.stripe_plan_id = settings.STRIPE_PLAN_MONTHLY_ID
        self.amount = MONTHLY_AMOUNT


class LessonsAnnualPlan:
    def __init__(self):
        self.stripe_plan_id = settings.STRIPE_PLAN_ANNUAL_ID
        self.amount = ANNUAL_AMOUNT


class LessonsPlan:
    def __init__(self, plan_id, automatic=False):
        """
        plan_id is either string 'm' (stands for monthly)
        or a string letter 'a' (which stands for annual)
        """
        if plan_id == 'm':
            self.plan = LessonsMonthPlan()
            self.id = 'm'
        elif plan_id == 'a':
            self.plan = LessonsAnnualPlan()
            self.id = 'a'
        else:
            raise ValueError('Invalid plan_id value')

        self.currency = 'usd'
        self.automatic = automatic

    @property
    def stripe_plan_id(self):
        return self.plan.stripe_plan_id

    @property
    def amount(self):
        return self.plan.amount

    @property
    def human_details(self):
        msg = "PRO account "

        if self.automatic in ('True', 'on'):
            if isinstance(self.plan, LessonsMonthPlan):
                msg += "with monthly subscription."
            elif isinstance(self.plan, LessonsAnnualPlan):
                msg += "with annual subscription."
        else:
            if isinstance(self.plan, LessonsMonthPlan):
                msg += " for a month."
            elif isinstance(self.plan, LessonsAnnualPlan):
                msg += " for a year."
            msg += " No subscription."

        return msg

    @property
    def human_message(self):
        dollars = self.plan.amount / 100
        return f"${dollars:.2f}"

