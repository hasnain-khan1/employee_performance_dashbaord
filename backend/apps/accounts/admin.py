"""
Admin configuration for the accounts app.

This module configures the Django admin interface
for user and profile management.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin configuration for the User model.
    
    Extends the default UserAdmin to include custom fields
    and improved display options.
    """
    
    list_display = [
        'employee_id', 'username', 'email', 'first_name', 'last_name',
        'role', 'status', 'department', 'is_active', 'date_joined'
    ]
    
    list_filter = [
        'role', 'status', 'department', 'is_active', 'is_staff', 'is_superuser',
        'date_joined', 'hire_date'
    ]
    
    search_fields = [
        'employee_id', 'username', 'email', 'first_name', 'last_name'
    ]
    
    ordering = ['employee_id']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {
            'fields': (
                'first_name', 'last_name', 'email', 'employee_id',
                'phone', 'bio', 'avatar'
            )
        }),
        ('Professional info', {
            'fields': (
                'role', 'status', 'hire_date', 'manager', 'department',
                'job_title'
            )
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            ),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'first_name', 'last_name',
                'password1', 'password2', 'role', 'employee_id'
            ),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'manager', 'department'
        )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for the UserProfile model.
    
    Provides interface for managing extended user profile information.
    """
    
    list_display = [
        'user', 'date_of_birth', 'timezone', 'language',
        'created_at', 'updated_at'
    ]
    
    list_filter = [
        'timezone', 'language', 'created_at', 'updated_at'
    ]
    
    search_fields = [
        'user__employee_id', 'user__username', 'user__email',
        'user__first_name', 'user__last_name'
    ]
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Personal Information', {
            'fields': (
                'date_of_birth', 'address', 'emergency_contact_name',
                'emergency_contact_phone'
            )
        }),
        ('Professional Information', {
            'fields': ('skills', 'certifications', 'education')
        }),
        ('Preferences', {
            'fields': (
                'timezone', 'language', 'notification_preferences'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('user')