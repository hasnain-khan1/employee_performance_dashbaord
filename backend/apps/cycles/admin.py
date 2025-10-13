"""
Admin configuration for the cycles app.
"""

from django.contrib import admin
from .models import (
    ReviewCycle, CycleParticipant, CycleTemplate,
    RatingScale, Competency, CycleRatingScale,
    CycleCompetency, TemplateCompetency
)


@admin.register(ReviewCycle)
class ReviewCycleAdmin(admin.ModelAdmin):
    """Admin interface for Review Cycle model."""
    
    list_display = ['name', 'cycle_type', 'status', 'start_date', 'end_date', 'created_by']
    list_filter = ['status', 'cycle_type', 'created_at']
    search_fields = ['name', 'description']
    date_hierarchy = 'start_date'
    ordering = ['-start_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'cycle_type', 'status')
        }),
        ('Cycle Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Goal Setting Period', {
            'fields': ('goal_setting_start', 'goal_setting_end')
        }),
        ('Review Periods', {
            'fields': (
                'self_review_start', 'self_review_end',
                'manager_review_start', 'manager_review_end'
            )
        }),
        ('Calibration (Optional)', {
            'fields': ('calibration_start', 'calibration_end'),
            'classes': ('collapse',)
        }),
        ('Configuration', {
            'fields': (
                'requires_goals', 'requires_self_review',
                'requires_manager_review', 'requires_peer_feedback',
                'max_peer_feedback'
            )
        }),
        ('Weighting', {
            'fields': ('goal_weight_percentage', 'competency_weight_percentage')
        }),
        ('Metadata', {
            'fields': ('created_by', 'is_active'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['activate_cycles']
    
    def activate_cycles(self, request, queryset):
        """Activate selected cycles."""
        for cycle in queryset:
            try:
                cycle.activate()
                self.message_user(request, f'Successfully activated cycle: {cycle.name}')
            except Exception as e:
                self.message_user(request, f'Error activating {cycle.name}: {str(e)}', level='error')
    activate_cycles.short_description = "Activate selected cycles (locks rating scales)"


@admin.register(RatingScale)
class RatingScaleAdmin(admin.ModelAdmin):
    """Admin interface for Rating Scale model."""
    
    list_display = ['name', 'scale_type', 'min_value', 'max_value', 'is_active']
    list_filter = ['scale_type', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(Competency)
class CompetencyAdmin(admin.ModelAdmin):
    """Admin interface for Competency model."""
    
    list_display = ['name', 'category', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['category', 'name']


@admin.register(CycleRatingScale)
class CycleRatingScaleAdmin(admin.ModelAdmin):
    """Admin interface for Cycle Rating Scale configuration."""
    
    list_display = ['cycle', 'rating_scale', 'is_locked', 'locked_at']
    list_filter = ['is_locked', 'created_at']
    search_fields = ['cycle__name', 'rating_scale__name']
    readonly_fields = ['is_locked', 'locked_at']


@admin.register(CycleCompetency)
class CycleCompetencyAdmin(admin.ModelAdmin):
    """Admin interface for Cycle Competency assignments."""
    
    list_display = ['cycle', 'competency', 'weight', 'is_required']
    list_filter = ['is_required', 'created_at']
    search_fields = ['cycle__name', 'competency__name']
    ordering = ['-weight']


@admin.register(CycleTemplate)
class CycleTemplateAdmin(admin.ModelAdmin):
    """Admin interface for Cycle Template model."""
    
    list_display = ['name', 'cycle_type', 'default_duration_days', 'is_active']
    list_filter = ['cycle_type', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'cycle_type')
        }),
        ('Duration Settings', {
            'fields': (
                'default_duration_days', 'goal_setting_days',
                'self_review_days', 'manager_review_days', 'calibration_days'
            )
        }),
        ('Requirements', {
            'fields': (
                'requires_goals', 'requires_self_review',
                'requires_manager_review', 'requires_peer_feedback',
                'max_peer_feedback'
            )
        }),
        ('Weighting', {
            'fields': ('goal_weight_percentage', 'competency_weight_percentage')
        }),
        ('Template Configuration', {
            'fields': ('default_rating_scale',)
        }),
        ('Status', {
            'fields': ('is_active',)
        })
    )


@admin.register(TemplateCompetency)
class TemplateCompetencyAdmin(admin.ModelAdmin):
    """Admin interface for Template Competency assignments."""
    
    list_display = ['template', 'competency', 'weight']
    list_filter = ['template']
    search_fields = ['template__name', 'competency__name']
    ordering = ['-weight']


@admin.register(CycleParticipant)
class CycleParticipantAdmin(admin.ModelAdmin):
    """Admin interface for Cycle Participant model."""
    
    list_display = ['employee', 'cycle', 'manager', 'goals_set', 'self_review_completed', 'manager_review_completed']
    list_filter = ['cycle', 'is_active', 'goals_set', 'self_review_completed', 'manager_review_completed']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    ordering = ['cycle', 'employee__employee_id']

