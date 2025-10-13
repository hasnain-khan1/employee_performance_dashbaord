"""
Admin configuration for the workflows app.
"""

from django.contrib import admin
from .models import WorkflowStep, WorkflowNotification, AuditLog


@admin.register(WorkflowStep)
class WorkflowStepAdmin(admin.ModelAdmin):
    """Admin interface for WorkflowStep model."""
    
    list_display = ['user', 'cycle', 'step_type', 'role', 'status', 'order', 'due_date']
    list_filter = ['status', 'role', 'step_type', 'cycle']
    search_fields = ['user__first_name', 'user__last_name', 'user__employee_id']
    ordering = ['cycle', 'role', 'order']
    date_hierarchy = 'created_at'


@admin.register(WorkflowNotification)
class WorkflowNotificationAdmin(admin.ModelAdmin):
    """Admin interface for WorkflowNotification model."""
    
    list_display = ['user', 'title', 'notification_type', 'is_read', 'sent_at']
    list_filter = ['is_read', 'notification_type', 'sent_at']
    search_fields = ['user__first_name', 'user__last_name', 'title', 'message']
    ordering = ['-sent_at']
    date_hierarchy = 'sent_at'


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin interface for AuditLog model."""
    
    list_display = ['user', 'action_type', 'model_name', 'object_id', 'ip_address', 'timestamp']
    list_filter = ['action_type', 'model_name', 'timestamp']
    search_fields = ['user__first_name', 'user__last_name', 'model_name']
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'
    readonly_fields = ['timestamp']

