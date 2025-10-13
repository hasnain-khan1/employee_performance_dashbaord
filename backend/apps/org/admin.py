"""
Admin configuration for the org app.

This module configures the Django admin interface
for organizational structure management.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Department, Team, TeamMembership, Position


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Department model.
    
    Provides interface for managing departments with
    hierarchical display and filtering options.
    """
    
    list_display = [
        'name', 'code', 'manager', 'parent_department',
        'employee_count', 'is_active', 'created_at'
    ]
    
    list_filter = [
        'is_active', 'parent_department', 'created_at'
    ]
    
    search_fields = [
        'name', 'code', 'description'
    ]
    
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description')
        }),
        ('Hierarchy', {
            'fields': ('parent_department', 'manager')
        }),
        ('Details', {
            'fields': ('budget', 'location', 'is_active')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'manager', 'parent_department'
        )


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Team model.
    
    Provides interface for managing teams with
    member information and filtering options.
    """
    
    list_display = [
        'name', 'department', 'team_lead', 'member_count',
        'is_active', 'created_at'
    ]
    
    list_filter = [
        'is_active', 'department', 'created_at'
    ]
    
    search_fields = [
        'name', 'description'
    ]
    
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'department', 'description')
        }),
        ('Leadership', {
            'fields': ('team_lead',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'department', 'team_lead'
        )


@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    """
    Admin configuration for the TeamMembership model.
    
    Provides interface for managing team memberships
    with user and team information.
    """
    
    list_display = [
        'user', 'team', 'role', 'joined_at', 'is_active'
    ]
    
    list_filter = [
        'is_active', 'role', 'joined_at', 'team__department'
    ]
    
    search_fields = [
        'user__employee_id', 'user__username', 'user__first_name',
        'user__last_name', 'team__name'
    ]
    
    ordering = ['-joined_at']
    
    fieldsets = (
        ('Membership', {
            'fields': ('user', 'team', 'role')
        }),
        ('Status', {
            'fields': ('is_active', 'joined_at')
        }),
    )
    
    readonly_fields = ['joined_at']
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'user', 'team', 'team__department'
        )


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Position model.
    
    Provides interface for managing job positions
    with salary and requirement information.
    """
    
    list_display = [
        'title', 'department', 'level', 'salary_range',
        'is_active', 'created_at'
    ]
    
    list_filter = [
        'is_active', 'level', 'department', 'created_at'
    ]
    
    search_fields = [
        'title', 'description', 'requirements'
    ]
    
    ordering = ['title']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'department', 'description')
        }),
        ('Requirements', {
            'fields': ('requirements', 'responsibilities', 'level')
        }),
        ('Compensation', {
            'fields': ('min_salary', 'max_salary')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('department')