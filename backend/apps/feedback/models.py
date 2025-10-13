"""
Feedback models for the EPMS system.

This module contains models for peer feedback management,
including feedback requests, responses, and evaluation.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class FeedbackRequest(models.Model):
    """
    Feedback request model for peer feedback.
    
    Represents a request for feedback from one employee
    to another during a review cycle.
    """
    
    # Status choices
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
    ]
    
    requester = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='feedback_requests_sent',
        help_text='Employee requesting feedback'
    )
    
    recipient = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='feedback_requests_received',
        help_text='Employee being asked for feedback'
    )
    
    cycle = models.ForeignKey(
        'cycles.ReviewCycle',
        on_delete=models.CASCADE,
        related_name='feedback_requests',
        help_text='Review cycle this feedback belongs to'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text='Current status of the feedback request'
    )
    
    message = models.TextField(
        help_text='Message from the requester'
    )
    
    due_date = models.DateTimeField(
        help_text='Due date for the feedback'
    )
    
    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the feedback was submitted'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Meta options for FeedbackRequest model."""
        verbose_name = 'Feedback Request'
        verbose_name_plural = 'Feedback Requests'
        ordering = ['-created_at']
        unique_together = ['requester', 'recipient', 'cycle']
    
    def __str__(self):
        """String representation of the feedback request."""
        return f"Feedback from {self.recipient.employee_id} to {self.requester.employee_id}"


class FeedbackResponse(models.Model):
    """
    Feedback response model.
    
    Represents the actual feedback response from
    a peer to the requester.
    """
    
    request = models.OneToOneField(
        FeedbackRequest,
        on_delete=models.CASCADE,
        related_name='response',
        help_text='Feedback request being responded to'
    )
    
    # Overall rating
    overall_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Overall rating (1-5)'
    )
    
    # Detailed feedback
    strengths = models.TextField(
        help_text='Strengths and positive aspects'
    )
    
    areas_for_improvement = models.TextField(
        help_text='Areas for improvement'
    )
    
    specific_examples = models.TextField(
        help_text='Specific examples and observations'
    )
    
    recommendations = models.TextField(
        help_text='Recommendations for development'
    )
    
    # Additional comments
    additional_comments = models.TextField(
        blank=True,
        help_text='Any additional comments'
    )
    
    # Anonymity
    is_anonymous = models.BooleanField(
        default=False,
        help_text='Whether the feedback is anonymous'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Meta options for FeedbackResponse model."""
        verbose_name = 'Feedback Response'
        verbose_name_plural = 'Feedback Responses'
        ordering = ['-created_at']
    
    def __str__(self):
        """String representation of the feedback response."""
        return f"Response for {self.request}"


class FeedbackTemplate(models.Model):
    """
    Feedback template model.
    
    Represents templates for feedback requests
    with predefined questions and structure.
    """
    
    name = models.CharField(
        max_length=200,
        help_text='Template name'
    )
    
    description = models.TextField(
        blank=True,
        help_text='Template description'
    )
    
    questions = models.JSONField(
        help_text='List of questions in the template'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Whether the template is active'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Meta options for FeedbackTemplate model."""
        verbose_name = 'Feedback Template'
        verbose_name_plural = 'Feedback Templates'
        ordering = ['name']
    
    def __str__(self):
        """String representation of the feedback template."""
        return self.name