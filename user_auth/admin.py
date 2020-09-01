from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ['username', 'first_name', 'last_name', 'email', 'phone', 'role', 'id_passport']
    filter_horizontal = ['object']

    fieldsets = (
        (None,
         {'fields': ('username', 'email', 'password')}),
        (('Личная информация'),
         {'fields': (
             'first_name', 'last_name', 'phone', 'role', 'id_passport', 'object')}),
        (('Права доступа'), {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
        ('Дата и время', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'first_name', 'last_name', 'phone', 'role', 'id_passport', 'object', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )