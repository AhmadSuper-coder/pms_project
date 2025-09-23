# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import PMSUser

@admin.register(PMSUser)
class PMSUserAdmin(UserAdmin):
    model = PMSUser
    # fields to display in admin list view
    list_display = ('id', 'email', 'full_name', 'sub_id', 'is_staff', 'is_active', 'is_superuser')
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    search_fields = ('email', 'full_name', 'sub_id')
    ordering = ('email',)
    
    # fields for creating user in admin
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'sub_id')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'sub_id', 'password1', 'password2', 'is_staff', 'is_active', 'is_superuser')}
        ),
    )
