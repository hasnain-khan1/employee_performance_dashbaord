"""
Analytics models for the EPMS system.

This module contains models for analytics, reporting,
and data visualization in the performance management system.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class Report(models.Model):
    """
    Report model for analytics and reporting.
    
    Represents generated reports with metadata
    and configuration information.
    """
    
    # Report type choices
    TYPE_CHOICES = [
        ('performance', 'Performance Report'),
        ('goals', 'Goals Report'),
        ('feedback', 'Feedback Report'),
        ('reviews', 'Reviews Report'),
        ('analytics', 'Analytics Report'),
        ('custom', 'Custom Report'),
    ]
    
    # Report status choices
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('generating', 'Generating'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    name = models.CharField(
        max_length=200,
        help_text='Report name'
    )
    
    description = models.TextField(
        blank=True,
        help_text='Report description'
    )
    
    report_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        help_text='Type of report'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text='Current status of the report'
    )
    
    # Report configuration
    parameters = models.JSONField(
        default=dict,
        help_text='Report parameters and filters'
    )
    
    # File information
    file_path = models.CharField(
        max_length=500,
        blank=True,
        help_text='Path to the generated report file'
    )
    
    file_size = models.BigIntegerField(
        null=True,
        blank=True,
        help_text='Size of the report file in bytes'
    )
    
    # Metadata
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='reports_created',
        help_text='User who created this report'
    )
    
    generated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the report was generated'
    )
    
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the report expires'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Meta options for Report model."""
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'
        ordering = ['-created_at']
    
    def __str__(self):
        """String representation of the report."""
        return self.name


class Dashboard(models.Model):
    """
    Dashboard model for analytics dashboards.
    
    Represents user-customizable dashboards
    with widgets and visualizations.
    """
    
    name = models.CharField(
        max_length=200,
        help_text='Dashboard name'
    )
    
    description = models.TextField(
        blank=True,
        help_text='Dashboard description'
    )
    
    owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='dashboards',
        help_text='Dashboard owner'
    )
    
    is_public = models.BooleanField(
        default=False,
        help_text='Whether the dashboard is public'
    )
    
    configuration = models.JSONField(
        default=dict,
        help_text='Dashboard configuration and layout'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Whether the dashboard is active'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Meta options for Dashboard model."""
        verbose_name = 'Dashboard'
        verbose_name_plural = 'Dashboards'
        ordering = ['-created_at']
    
    def __str__(self):
        """String representation of the dashboard."""
        return self.name


class Metric(models.Model):
    """
    Metric model for performance metrics.
    
    Represents key performance indicators
    and metrics tracked in the system.
    """
    
    # Metric type choices
    TYPE_CHOICES = [
        ('goal_completion', 'Goal Completion Rate'),
        ('review_completion', 'Review Completion Rate'),
        ('feedback_response', 'Feedback Response Rate'),
        ('performance_rating', 'Average Performance Rating'),
        ('goal_achievement', 'Goal Achievement Score'),
        ('custom', 'Custom Metric'),
    ]
    
    name = models.CharField(
        max_length=200,
        help_text='Metric name'
    )
    
    description = models.TextField(
        blank=True,
        help_text='Metric description'
    )
    
    metric_type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        help_text='Type of metric'
    )
    
    calculation_method = models.TextField(
        help_text='How the metric is calculated'
    )
    
    unit = models.CharField(
        max_length=50,
        blank=True,
        help_text='Unit of measurement'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Whether the metric is active'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Meta options for Metric model."""
        verbose_name = 'Metric'
        verbose_name_plural = 'Metrics'
        ordering = ['name']
    
    def __str__(self):
        """String representation of the metric."""
        return self.name