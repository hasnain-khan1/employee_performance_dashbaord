"""
Serializers for the workflows app.
"""

from rest_framework import serializers
from .models import WorkflowStep, WorkflowNotification, AuditLog


class WorkflowStepSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowStep model."""
    
    step_type_display = serializers.CharField(source='get_step_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = WorkflowStep
        fields = [
            'id', 'user', 'cycle', 'step_type', 'step_type_display',
            'role', 'role_display', 'status', 'status_display', 'order',
            'started_at', 'completed_at', 'due_date', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class WorkflowNotificationSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowNotification model."""
    
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    
    class Meta:
        model = WorkflowNotification
        fields = [
            'id', 'user', 'workflow_step', 'notification_type',
            'notification_type_display', 'title', 'message',
            'is_read', 'sent_at', 'read_at'
        ]
        read_only_fields = ['sent_at']


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for AuditLog model."""
    
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_name', 'action_type', 'action_type_display',
            'model_name', 'object_id', 'changes', 'ip_address',
            'user_agent', 'timestamp'
        ]
        read_only_fields = ['timestamp']

