"""
Admin configuration for the goals app.
"""

from django.contrib import admin
from .models import (
    Goal, GoalUpdate, GoalCategory, GoalTemplate,
    GoalVersion, BusinessObjective, GoalAlignment, GoalFeedback
)


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    """Admin interface for Goal model."""
    
    list_display = ['title', 'employee', 'status', 'priority', 'weight', 'target_date', 'approved_by', 'created_at']
    list_filter = ['status', 'priority', 'goal_type', 'cycle', 'created_at']
    search_fields = ['title', 'description', 'employee__first_name', 'employee__last_name', 'employee__employee_id']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    readonly_fields = ['created_at', 'updated_at', 'approved_at', 'last_updated', 'progress_percentage']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'employee', 'cycle', 'status', 'priority', 'goal_type')
        }),
        ('SMART Criteria', {
            'fields': ('specific', 'measurable', 'achievable', 'relevant', 'time_bound')
        }),
        ('Metrics', {
            'fields': ('metric', 'target_value', 'current_value', 'unit')
        }),
        ('Timeline', {
            'fields': ('start_date', 'target_date', 'completed_date')
        }),
        ('Progress & Weighting', {
            'fields': ('weight', 'progress_percentage')
        }),
        ('Approval', {
            'fields': ('approved_by', 'approved_at'),
            'classes': ('collapse',)
        }),
        ('Additional', {
            'fields': ('notes', 'created_at', 'updated_at', 'last_updated'),
            'classes': ('collapse',)
        })
    )


@admin.register(GoalFeedback)
class GoalFeedbackAdmin(admin.ModelAdmin):
    """Admin interface for GoalFeedback model."""
    
    list_display = ['goal', 'manager', 'feedback_type', 'smart_compliance_score', 'created_at']
    list_filter = ['feedback_type', 'challenge_level', 'created_at']
    search_fields = ['goal__title', 'manager__first_name', 'manager__last_name', 'comments']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    readonly_fields = ['created_at', 'updated_at', 'smart_compliance_score']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('goal', 'manager', 'feedback_type')
        }),
        ('Feedback', {
            'fields': ('comments', 'suggested_modifications')
        }),
        ('SMART Criteria Review', {
            'fields': (
                'smart_specific', 'smart_measurable', 'smart_achievable',
                'smart_relevant', 'smart_time_bound', 'smart_compliance_score'
            )
        }),
        ('Assessment', {
            'fields': ('alignment_score', 'challenge_level')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(GoalUpdate)
class GoalUpdateAdmin(admin.ModelAdmin):
    """Admin interface for GoalUpdate model."""
    
    list_display = ['goal', 'updated_by', 'progress_percentage', 'created_at']
    list_filter = ['created_at']
    search_fields = ['goal__title', 'updated_by__first_name', 'updated_by__last_name']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(GoalCategory)
class GoalCategoryAdmin(admin.ModelAdmin):
    """Admin interface for GoalCategory model."""
    
    list_display = ['name', 'color', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(GoalTemplate)
class GoalTemplateAdmin(admin.ModelAdmin):
    """Admin interface for GoalTemplate model."""
    
    list_display = ['name', 'goal_type', 'category', 'usage_count', 'is_active', 'created_by']
    list_filter = ['goal_type', 'category', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['-usage_count', 'name']
    
    readonly_fields = ['usage_count', 'created_at', 'updated_at']


@admin.register(GoalVersion)
class GoalVersionAdmin(admin.ModelAdmin):
    """Admin interface for GoalVersion model."""
    
    list_display = ['goal', 'version_number', 'change_type', 'changed_by', 'created_at']
    list_filter = ['change_type', 'created_at']
    search_fields = ['goal__title', 'changed_by__first_name', 'changed_by__last_name']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    readonly_fields = ['created_at']


@admin.register(BusinessObjective)
class BusinessObjectiveAdmin(admin.ModelAdmin):
    """Admin interface for BusinessObjective model."""
    
    list_display = ['name', 'priority', 'status', 'target_date', 'owner', 'is_active']
    list_filter = ['priority', 'status', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    date_hierarchy = 'target_date'
    ordering = ['-priority', 'target_date']


@admin.register(GoalAlignment)
class GoalAlignmentAdmin(admin.ModelAdmin):
    """Admin interface for GoalAlignment model."""
    
    list_display = ['goal', 'objective', 'alignment_strength', 'created_at']
    list_filter = ['alignment_strength', 'created_at']
    search_fields = ['goal__title', 'objective__name']
    ordering = ['-created_at']

