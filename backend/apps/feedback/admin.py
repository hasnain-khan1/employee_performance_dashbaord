"""
Django admin configuration for feedback app.
"""

from django.contrib import admin
from .models import FeedbackRequest, FeedbackResponse, FeedbackTemplate, ManagerFeedback


@admin.register(FeedbackRequest)
class FeedbackRequestAdmin(admin.ModelAdmin):
    """Admin interface for FeedbackRequest model."""
    list_display = ['id', 'requester', 'recipient', 'cycle', 'status', 'due_date', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['requester__email', 'recipient__email']
    readonly_fields = ['created_at', 'updated_at', 'submitted_at']
    date_hierarchy = 'created_at'


@admin.register(FeedbackResponse)
class FeedbackResponseAdmin(admin.ModelAdmin):
    """Admin interface for FeedbackResponse model."""
    list_display = ['id', 'request', 'overall_rating', 'is_anonymous', 'created_at']
    list_filter = ['is_anonymous', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(FeedbackTemplate)
class FeedbackTemplateAdmin(admin.ModelAdmin):
    """Admin interface for FeedbackTemplate model."""
    list_display = ['id', 'name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ManagerFeedback)
class ManagerFeedbackAdmin(admin.ModelAdmin):
    """Admin interface for ManagerFeedback model."""
    list_display = ['id', 'manager', 'employee', 'feedback_type', 'subject', 'is_acknowledged', 'created_at']
    list_filter = ['feedback_type', 'visibility', 'is_acknowledged', 'created_at']
    search_fields = ['manager__email', 'employee__email', 'subject', 'feedback']
    readonly_fields = ['created_at', 'updated_at', 'acknowledged_at']
    date_hierarchy = 'created_at'

