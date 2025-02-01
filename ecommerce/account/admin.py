# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from ecommerce.account.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username',
        'name',
        'phone_number_1',
        'phone_number_2',
        'is_staff',
        'is_active'
    )

    list_filter = (
        'is_staff',
        'is_superuser',
        'is_active',
        'province',
    )

    # Add search fields
    search_fields = (
        'username',
        'name',
        'phone_number_1',
        'phone_number_2',
    )

    # Control how fields are displayed when editing a user
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {
            'fields': (
                'name',
                'dob',
                'address1',
                'phone_number_1',
                'phone_number_2',
                'province'
            )
        }),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            )
        }),
        (_('Important dates'), {
            'fields': (
                'last_login',
                'date_joined'
            )
        }),
    )

    # Control the fields shown when creating a new user from the admin site
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'name',
                'password1',
                'password2',
                'is_staff',
                'is_active'
            ),
        }),
    )

    ordering = ('username',)

