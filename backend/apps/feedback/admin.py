"""
Django admin configuration for feedback app.
"""

from django.contrib import admin
from .models import (
    FeedbackRequest, FeedbackResponse, FeedbackTemplate,
    PeerReviewer, ContentPolicyRule
)


@admin.register(FeedbackRequest)
class FeedbackRequestAdmin(admin.ModelAdmin):
    """Admin interface for FeedbackRequest model."""
    list_display = ['id', 'requester', 'title', 'status', 'deadline', 'completion_percentage', 'created_at']
    list_filter = ['status', 'allow_anonymous', 'created_at']
    search_fields = ['requester__email', 'title', 'description']
    readonly_fields = ['created_at', 'updated_at', 'completion_percentage', 'is_expired']
    date_hierarchy = 'created_at'


@admin.register(PeerReviewer)
class PeerReviewerAdmin(admin.ModelAdmin):
    """Admin interface for PeerReviewer model."""
    list_display = ['id', 'feedback_request', 'reviewer', 'status', 'invited_at', 'responded_at']
    list_filter = ['status', 'invited_at']
    search_fields = ['feedback_request__title', 'reviewer__email']
    readonly_fields = ['invited_at', 'responded_at', 'reminder_sent_count', 'last_reminder_sent', 'is_overdue']


@admin.register(FeedbackResponse)
class FeedbackResponseAdmin(admin.ModelAdmin):
    """Admin interface for FeedbackResponse model."""
    list_display = ['id', 'peer_reviewer', 'overall_rating', 'average_rating', 'is_anonymous', 'is_submitted', 'submitted_at']
    list_filter = ['is_anonymous', 'is_submitted', 'content_policy_approved', 'submitted_at']
    search_fields = ['peer_reviewer__reviewer__email', 'strengths', 'development_areas']
    readonly_fields = ['created_at', 'updated_at', 'submitted_at', 'average_rating', 'content_policy_violations']
    date_hierarchy = 'submitted_at'


@admin.register(FeedbackTemplate)
class FeedbackTemplateAdmin(admin.ModelAdmin):
    """Admin interface for FeedbackTemplate model."""
    list_display = ['id', 'name', 'is_active', 'is_default', 'created_at']
    list_filter = ['is_active', 'is_default', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ContentPolicyRule)
class ContentPolicyRuleAdmin(admin.ModelAdmin):
    """Admin interface for ContentPolicyRule model."""
    list_display = ['id', 'name', 'rule_type', 'severity', 'is_active', 'auto_block', 'created_at']
    list_filter = ['rule_type', 'severity', 'is_active', 'auto_block', 'created_at']
    search_fields = ['name', 'warning_message']
    readonly_fields = ['created_at', 'updated_at']


