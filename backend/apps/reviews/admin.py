"""
Admin configuration for the reviews app.

This module contains Django admin configurations for self-review and manager review management.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    SelfReview, ManagerReview, ReviewAttachment, ReviewAuditTrail,
    SelfReviewSection, EvidenceLink, SelfReviewDraft, SelfReviewAuditTrail,
    SelfReviewTemplate
)


@admin.register(SelfReview)
class SelfReviewAdmin(admin.ModelAdmin):
    """Admin configuration for SelfReview model."""
    
    list_display = [
        'id', 'employee', 'cycle', 'status', 'completion_percentage',
        'prerequisites_met', 'created_at', 'submitted_at'
    ]
    list_filter = [
        'status', 'prerequisites_met', 'cycle', 'created_at', 'submitted_at'
    ]
    search_fields = [
        'employee__first_name', 'employee__last_name', 'employee__email',
        'cycle__name'
    ]
    readonly_fields = [
        'completion_percentage', 'created_at', 'updated_at',
        'submitted_at', 'last_auto_save'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Review Information', {
            'fields': ('employee', 'cycle', 'status', 'completion_percentage')
        }),
        ('Prerequisites', {
            'fields': ('goals_approved', 'peer_feedback_received', 'prerequisites_met')
        }),
        ('Content Sections', {
            'fields': (
                'goal_achievement_summary', 'key_accomplishments',
                'behavioral_competencies', 'development_areas', 'career_aspirations'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'submitted_at', 'last_auto_save'),
            'classes': ('collapse',)
        })
    )


@admin.register(ManagerReview)
class ManagerReviewAdmin(admin.ModelAdmin):
    """Admin configuration for ManagerReview model."""
    
    list_display = [
        'id', 'employee', 'manager', 'cycle', 'overall_rating',
        'status', 'is_locked', 'created_at', 'submitted_at'
    ]
    list_filter = [
        'status', 'is_locked', 'cycle', 'overall_rating',
        'created_at', 'submitted_at', 'approved_at'
    ]
    search_fields = [
        'employee__first_name', 'employee__last_name', 'employee__email',
        'manager__first_name', 'manager__last_name', 'cycle__name'
    ]
    readonly_fields = [
        'average_competency_rating', 'is_complete', 'created_at',
        'updated_at', 'submitted_at', 'approved_at', 'last_auto_save'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Review Information', {
            'fields': ('employee', 'manager', 'cycle', 'status', 'is_locked')
        }),
        ('Review Period', {
            'fields': ('review_period_start', 'review_period_end')
        }),
        ('Goals & Achievements', {
            'fields': ('goals_achievements',)
        }),
        ('Competency Ratings', {
            'fields': (
                'communication_rating', 'collaboration_rating',
                'leadership_rating', 'problem_solving_rating',
                'adaptability_rating', 'overall_rating'
            )
        }),
        ('Narrative Sections', {
            'fields': (
                'performance_summary', 'strengths', 'development_areas',
                'career_recommendations'
            ),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('comments', 'private_notes', 'development_notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'submitted_at', 'approved_at', 'last_auto_save'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'employee', 'manager', 'cycle'
        )


@admin.register(ReviewAttachment)
class ReviewAttachmentAdmin(admin.ModelAdmin):
    """Admin configuration for ReviewAttachment model."""
    
    list_display = [
        'id', 'file_name', 'manager_review', 'file_type', 'file_size',
        'uploaded_by', 'uploaded_at'
    ]
    list_filter = ['file_type', 'uploaded_at']
    search_fields = [
        'file_name', 'description', 'manager_review__employee__first_name',
        'manager_review__employee__last_name', 'uploaded_by__first_name',
        'uploaded_by__last_name'
    ]
    readonly_fields = ['file_size', 'uploaded_at']
    date_hierarchy = 'uploaded_at'
    ordering = ['-uploaded_at']
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'manager_review__employee', 'manager_review__manager', 'uploaded_by'
        )


@admin.register(ReviewAuditTrail)
class ReviewAuditTrailAdmin(admin.ModelAdmin):
    """Admin configuration for ReviewAuditTrail model."""
    
    list_display = [
        'id', 'manager_review', 'action', 'user', 'timestamp',
        'ip_address'
    ]
    list_filter = ['action', 'timestamp', 'ip_address']
    search_fields = [
        'manager_review__employee__first_name', 'manager_review__employee__last_name',
        'user__first_name', 'user__last_name', 'change_summary'
    ]
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'manager_review__employee', 'manager_review__manager', 'user'
        )


@admin.register(SelfReviewSection)
class SelfReviewSectionAdmin(admin.ModelAdmin):
    """Admin configuration for SelfReviewSection model."""
    
    list_display = [
        'id', 'self_review', 'section_type', 'word_count',
        'is_completed', 'created_at'
    ]
    list_filter = ['section_type', 'is_completed', 'created_at']
    search_fields = [
        'self_review__employee__first_name', 'self_review__employee__last_name'
    ]
    readonly_fields = ['word_count', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(EvidenceLink)
class EvidenceLinkAdmin(admin.ModelAdmin):
    """Admin configuration for EvidenceLink model."""
    
    list_display = [
        'id', 'self_review', 'link_type', 'title', 'created_at'
    ]
    list_filter = ['link_type', 'created_at']
    search_fields = [
        'title', 'description', 'self_review__employee__first_name',
        'self_review__employee__last_name'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(SelfReviewDraft)
class SelfReviewDraftAdmin(admin.ModelAdmin):
    """Admin configuration for SelfReviewDraft model."""
    
    list_display = [
        'id', 'self_review', 'section_type', 'word_count',
        'is_auto_save', 'save_reason', 'created_at'
    ]
    list_filter = ['section_type', 'is_auto_save', 'save_reason', 'created_at']
    search_fields = [
        'self_review__employee__first_name', 'self_review__employee__last_name'
    ]
    readonly_fields = ['word_count', 'created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(SelfReviewAuditTrail)
class SelfReviewAuditTrailAdmin(admin.ModelAdmin):
    """Admin configuration for SelfReviewAuditTrail model."""
    
    list_display = [
        'id', 'self_review', 'action', 'section_type', 'user',
        'timestamp', 'ip_address'
    ]
    list_filter = ['action', 'section_type', 'timestamp', 'ip_address']
    search_fields = [
        'self_review__employee__first_name', 'self_review__employee__last_name',
        'user__first_name', 'user__last_name', 'changes_summary'
    ]
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']


@admin.register(SelfReviewTemplate)
class SelfReviewTemplateAdmin(admin.ModelAdmin):
    """Admin configuration for SelfReviewTemplate model."""
    
    list_display = [
        'id', 'name', 'is_active', 'is_default', 'created_by', 'created_at'
    ]
    list_filter = ['is_active', 'is_default', 'created_at']
    search_fields = ['name', 'description', 'created_by__first_name', 'created_by__last_name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    ordering = ['-is_default', 'name']
    
    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'description', 'is_active', 'is_default')
        }),
        ('Configuration', {
            'fields': ('sections_config', 'writing_guidelines', 'examples'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
