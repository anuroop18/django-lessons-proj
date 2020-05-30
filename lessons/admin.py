from datetime import date

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .models import (Contact, Course, Lesson, LessonGroup, Subscription,
                     UserProfile)


class ProfileInline(admin.StackedInline):
    model = UserProfile
    fields = ('discount_enddate', )


class IsPROListFilter(admin.SimpleListFilter):
    title = _('is PRO')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'pro'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('yes', _('Yes')),
            ('no', _('No')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        _today = date.today()
        if self.value() == 'yes':
            return queryset.filter(profile__pro_enddate__gte=_today)
        if self.value() == 'no':
            return queryset.filter(profile__pro_enddate__lte=_today)


class HasDiscountListFilter(admin.SimpleListFilter):
    title = _('Has discount')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'discount'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Yes')),
            ('no', _('No')),
        )

    def queryset(self, request, queryset):
        _today = date.today()
        if self.value() == 'yes':
            return queryset.filter(profile__discount_enddate__gte=_today)
        if self.value() == 'no':
            return queryset.filter(profile__discount_enddate__lte=_today)


class CustomUserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'is_pro',
        'has_discount',
        'is_staff',
        'first_name',
        'last_name',
    )
    inlines = [
        ProfileInline,
    ]
    list_filter = UserAdmin.list_filter + (
        IsPROListFilter,
        HasDiscountListFilter,
    )

    def is_pro(self, obj):
        return obj.profile.is_pro_user()

    is_pro.boolean = True

    def has_discount(self, obj):
        return obj.profile.discount

    has_discount.boolean = True


class ContactAdmin(admin.ModelAdmin):
    list_display = ('email', 'subject')


class SubscriptionAdmin(admin.ModelAdmin):
    pass


class CourseAdmin(admin.ModelAdmin):
    pass


class LessonAdmin(admin.ModelAdmin):
    pass


class LessonGroupAdmin(admin.ModelAdmin):
    pass


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(LessonGroup, LessonGroupAdmin)
