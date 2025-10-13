"""
Workflow tracking models for the EPMS system.

This module contains models for tracking user progress through
the performance review workflow.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class WorkflowStep(models.Model):
    """
    Workflow step model for tracking performance review stages.
    
    Represents individual steps in the performance review workflow
    for employees, managers, and HR.
    """
    
    STEP_STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
        ('overdue', 'Overdue'),
    ]
    
    ROLE_CHOICES = [
        ('employee', 'Employee'),
        ('manager', 'Manager'),
        ('hr', 'HR Administrator'),
        ('admin', 'Admin'),
    ]
    
    STEP_TYPE_CHOICES = [
        ('goal_creation', 'Goal Creation'),
        ('goal_approval', 'Goal Approval'),
        ('goal_progress', 'Goal Progress Tracking'),
        ('peer_feedback_request', 'Peer Feedback Request'),
        ('peer_feedback_submission', 'Peer Feedback Submission'),
        ('self_review', 'Self Review'),
        ('manager_review', 'Manager Review'),
        ('calibration', 'Calibration'),
        ('final_review', 'Final Review'),
    ]
    
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='workflow_steps',
        help_text='User for this workflow step'
    )
    
    cycle = models.ForeignKey(
        'cycles.ReviewCycle',
        on_delete=models.CASCADE,
        related_name='workflow_steps',
        help_text='Review cycle for this workflow step'
    )
    
    step_type = models.CharField(
        max_length=50,
        choices=STEP_TYPE_CHOICES,
        help_text='Type of workflow step'
    )
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        help_text='Role for this workflow step'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STEP_STATUS_CHOICES,
        default='not_started',
        help_text='Current status of the workflow step'
    )
    
    order = models.PositiveIntegerField(
        default=0,
        help_text='Order of this step in the workflow'
    )
    
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When this step was started'
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When this step was completed'
    )
    
    due_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Due date for this step'
    )
    
    notes = models.TextField(
        blank=True,
        help_text='Notes about this workflow step'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Meta options for WorkflowStep model."""
        verbose_name = 'Workflow Step'
        verbose_name_plural = 'Workflow Steps'
        unique_together = ['user', 'cycle', 'step_type']
        ordering = ['cycle', 'role', 'order']
        indexes = [
            models.Index(fields=['user', 'cycle', 'status']),
            models.Index(fields=['cycle', 'role', 'status']),
        ]
    
    def __str__(self):
        """String representation of the workflow step."""
        return f"{self.user.full_name} - {self.get_step_type_display()} ({self.get_status_display()})"


class WorkflowNotification(models.Model):
    """
    Workflow notification model for automated reminders.
    
    Represents notifications sent to users about workflow steps.
    """
    
    NOTIFICATION_TYPE_CHOICES = [
        ('reminder', 'Reminder'),
        ('deadline_alert', 'Deadline Alert'),
        ('overdue_alert', 'Overdue Alert'),
        ('completion', 'Completion Notification'),
        ('approval_request', 'Approval Request'),
        ('approval_response', 'Approval Response'),
    ]
    
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='workflow_notifications',
        help_text='User to notify'
    )
    
    workflow_step = models.ForeignKey(
        WorkflowStep,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True,
        help_text='Related workflow step'
    )
    
    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPE_CHOICES,
        help_text='Type of notification'
    )
    
    title = models.CharField(
        max_length=200,
        help_text='Notification title'
    )
    
    message = models.TextField(
        help_text='Notification message'
    )
    
    is_read = models.BooleanField(
        default=False,
        help_text='Whether the notification has been read'
    )
    
    sent_at = models.DateTimeField(
        auto_now_add=True,
        help_text='When the notification was sent'
    )
    
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the notification was read'
    )
    
    class Meta:
        """Meta options for WorkflowNotification model."""
        verbose_name = 'Workflow Notification'
        verbose_name_plural = 'Workflow Notifications'
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['-sent_at']),
        ]
    
    def __str__(self):
        """String representation of the notification."""
        return f"{self.user.full_name} - {self.title}"


class AuditLog(models.Model):
    """
    Audit log model for compliance and security.
    
    Records all significant actions in the system for compliance.
    """
    
    ACTION_TYPE_CHOICES = [
        ('create', 'Create'),
        ('read', 'Read'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('submit', 'Submit'),
        ('export', 'Export'),
    ]
    
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs',
        help_text='User who performed the action'
    )
    
    action_type = models.CharField(
        max_length=20,
        choices=ACTION_TYPE_CHOICES,
        help_text='Type of action performed'
    )
    
    model_name = models.CharField(
        max_length=100,
        help_text='Name of the model affected'
    )
    
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='ID of the object affected'
    )
    
    changes = models.JSONField(
        null=True,
        blank=True,
        help_text='JSON representation of changes made'
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='IP address of the user'
    )
    
    user_agent = models.TextField(
        blank=True,
        help_text='User agent string'
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text='When the action was performed'
    )
    
    class Meta:
        """Meta options for AuditLog model."""
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['-timestamp']),
        ]
    
    def __str__(self):
        """String representation of the audit log."""
        return f"{self.user.full_name if self.user else 'System'} - {self.action_type} {self.model_name}"

