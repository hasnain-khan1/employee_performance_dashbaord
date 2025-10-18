"""
Models for the feedback app.

This module contains models for peer feedback collection,
including request management, response tracking, and content policy enforcement.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.conf import settings

User = get_user_model()


class FeedbackRequest(models.Model):
    """
    Model representing a peer feedback request.
    """
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled')
    ]
    
    # Request details
    requester = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='feedback_requests_sent',
        help_text="Employee requesting feedback"
    )
    cycle = models.ForeignKey(
        'cycles.ReviewCycle',
        on_delete=models.CASCADE,
        related_name='feedback_requests',
        help_text="Performance cycle for this feedback"
    )
    
    # Request configuration
    title = models.CharField(
        max_length=200,
        default="Feedback Request",
        help_text="Title for this feedback request"
    )
    description = models.TextField(blank=True, help_text="Optional description")
    deadline = models.DateTimeField(
        default=timezone.now,
        help_text="Deadline for feedback submission"
    )
    
    # Status and tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text="Current status of the feedback request"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Configuration
    allow_anonymous = models.BooleanField(
        default=True,
        help_text="Whether anonymous feedback is allowed"
    )
    min_peers = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Minimum number of peer reviewers required"
    )
    max_peers = models.IntegerField(
        default=5,
        validators=[MaxValueValidator(5)],
        help_text="Maximum number of peer reviewers allowed"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Feedback Request"
        verbose_name_plural = "Feedback Requests"
    
    def __str__(self):
        return f"Feedback Request: {self.title} - {self.requester.get_full_name()}"
    
    @property
    def is_expired(self):
        """Check if the feedback request has expired."""
        return timezone.now() > self.deadline
    
    @property
    def completion_percentage(self):
        """Calculate completion percentage based on responses."""
        total_peers = self.peer_reviewers.count()
        if total_peers == 0:
            return 0
        completed_responses = self.peer_reviewers.filter(
            response__isnull=False,
            response__is_submitted=True
        ).count()
        return (completed_responses / total_peers) * 100


class PeerReviewer(models.Model):
    """
    Model representing a peer reviewer for a feedback request.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('declined', 'Declined'),
        ('expired', 'Expired')
    ]
    
    # Relationships
    feedback_request = models.ForeignKey(
        FeedbackRequest,
        on_delete=models.CASCADE,
        related_name='peer_reviewers',
        help_text="The feedback request this reviewer is part of"
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='peer_reviews_received',
        help_text="The peer reviewer"
    )
    
    # Reviewer details
    relationship_context = models.TextField(
        blank=True,
        help_text="Context about the working relationship"
    )
    personal_message = models.TextField(
        blank=True,
        help_text="Personal message from requester to reviewer"
    )
    
    # Status and tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Status of this peer review"
    )
    invited_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    # Reminder tracking
    reminder_sent_count = models.IntegerField(default=0)
    last_reminder_sent = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['feedback_request', 'reviewer']
        ordering = ['invited_at']
        verbose_name = "Peer Reviewer"
        verbose_name_plural = "Peer Reviewers"
    
    def __str__(self):
        return f"{self.reviewer.get_full_name()} - {self.feedback_request.title}"
    
    @property
    def is_overdue(self):
        """Check if this peer review is overdue."""
        return (
            self.status in ['pending', 'in_progress'] and
            timezone.now() > self.feedback_request.deadline
        )


class FeedbackResponse(models.Model):
    """
    Model representing a peer's feedback response.
    """
    
    # Relationships
    peer_reviewer = models.OneToOneField(
        PeerReviewer,
        on_delete=models.CASCADE,
        related_name='response',
        null=True,
        blank=True,
        help_text="The peer reviewer who submitted this response"
    )
    
    # Response data
    is_submitted = models.BooleanField(
        default=False,
        help_text="Whether the response has been submitted"
    )
    is_anonymous = models.BooleanField(
        default=False,
        help_text="Whether the reviewer chose to remain anonymous"
    )
    
    # Behavioral competencies (1-5 scale)
    communication_rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Communication skills rating"
    )
    collaboration_rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Collaboration skills rating"
    )
    leadership_rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Leadership skills rating"
    )
    problem_solving_rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Problem-solving skills rating"
    )
    adaptability_rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Adaptability rating"
    )
    
    # Text feedback
    strengths = models.TextField(
        blank=True,
        help_text="Strengths and positive contributions"
    )
    development_areas = models.TextField(
        blank=True,
        help_text="Areas for development and improvement"
    )
    collaboration_examples = models.TextField(
        blank=True,
        help_text="Specific examples of working together"
    )
    overall_rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Overall performance rating"
    )
    additional_comments = models.TextField(
        blank=True,
        help_text="Additional comments or observations"
    )
    
    # Content policy tracking
    content_policy_violations = models.JSONField(
        default=list,
        blank=True,
        help_text="List of content policy violations found"
    )
    content_policy_approved = models.BooleanField(
        default=False,
        help_text="Whether content policy review is approved"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Feedback Response"
        verbose_name_plural = "Feedback Responses"
    
    def __str__(self):
        return f"Response from {self.peer_reviewer.reviewer.get_full_name()}"
    
    @property
    def average_rating(self):
        """Calculate average of all competency ratings."""
        ratings = [
            self.communication_rating,
            self.collaboration_rating,
            self.leadership_rating,
            self.problem_solving_rating,
            self.adaptability_rating
        ]
        valid_ratings = [r for r in ratings if r is not None]
        if not valid_ratings:
            return None
        return sum(valid_ratings) / len(valid_ratings)


class ContentPolicyRule(models.Model):
    """
    Model for content policy rules and enforcement.
    """
    
    RULE_TYPES = [
        ('profanity', 'Profanity Filter'),
        ('bias', 'Bias Detection'),
        ('tone', 'Tone Analysis'),
        ('length', 'Length Requirements'),
        ('professional', 'Professional Language')
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ]
    
    # Rule configuration
    name = models.CharField(max_length=100, help_text="Name of the policy rule")
    rule_type = models.CharField(
        max_length=20,
        choices=RULE_TYPES,
        help_text="Type of content policy rule"
    )
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_LEVELS,
        default='medium',
        help_text="Severity level of violations"
    )
    
    # Rule content
    keywords = models.JSONField(
        default=list,
        help_text="Keywords or phrases to flag"
    )
    patterns = models.JSONField(
        default=list,
        help_text="Regex patterns for detection"
    )
    min_length = models.IntegerField(
        null=True, blank=True,
        help_text="Minimum length requirement"
    )
    max_length = models.IntegerField(
        null=True, blank=True,
        help_text="Maximum length limit"
    )
    
    # Configuration
    is_active = models.BooleanField(default=True)
    auto_block = models.BooleanField(
        default=False,
        help_text="Whether to automatically block submission"
    )
    warning_message = models.TextField(
        help_text="Message to show when rule is violated"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='content_policy_rules_created'
    )
    
    class Meta:
        ordering = ['severity', 'name']
        verbose_name = "Content Policy Rule"
        verbose_name_plural = "Content Policy Rules"
    
    def __str__(self):
        return f"{self.name} ({self.get_severity_display()})"


class FeedbackTemplate(models.Model):
    """
    Model for standardized feedback templates.
    """
    
    # Template details
    name = models.CharField(max_length=100, help_text="Template name")
    description = models.TextField(blank=True, help_text="Template description")
    
    # Template content
    competencies = models.JSONField(
        default=list,
        help_text="List of competencies to evaluate"
    )
    questions = models.JSONField(
        default=list,
        help_text="Standardized questions for feedback"
    )
    rating_scale = models.JSONField(
        default=dict,
        help_text="Rating scale configuration"
    )
    
    # Configuration
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(
        default=False,
        help_text="Whether this is the default template"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='feedback_templates_created'
    )
    
    class Meta:
        ordering = ['-is_default', 'name']
        verbose_name = "Feedback Template"
        verbose_name_plural = "Feedback Templates"
    
    def __str__(self):
        return self.name


class ManagerFeedback(models.Model):
    """
    Model for manager-to-employee feedback.
    """
    
    FEEDBACK_TYPE_CHOICES = [
        ('recognition', 'Recognition'),
        ('constructive', 'Constructive'),
        ('coaching', 'Coaching'),
        ('development', 'Development'),
        ('general', 'General')
    ]
    
    VISIBILITY_CHOICES = [
        ('private', 'Private (Manager & Employee only)'),
        ('hr', 'Visible to HR'),
        ('public', 'Public (Visible to all)')
    ]
    
    # Relationships
    manager = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='manager_feedback_given',
        help_text="Manager providing the feedback"
    )
    employee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='manager_feedback_received',
        help_text="Employee receiving the feedback"
    )
    cycle = models.ForeignKey(
        'cycles.ReviewCycle',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='manager_feedback',
        help_text="Optional: Associated review cycle"
    )
    
    # Feedback content
    feedback_type = models.CharField(
        max_length=20,
        choices=FEEDBACK_TYPE_CHOICES,
        default='general',
        help_text="Type of feedback"
    )
    subject = models.CharField(
        max_length=200,
        help_text="Brief subject/title of the feedback"
    )
    feedback = models.TextField(
        help_text="Detailed feedback content"
    )
    strengths = models.TextField(
        blank=True,
        help_text="Specific strengths observed (optional)"
    )
    areas_for_improvement = models.TextField(
        blank=True,
        help_text="Areas for growth and development (optional)"
    )
    action_items = models.TextField(
        blank=True,
        help_text="Suggested action items or next steps (optional)"
    )
    
    # Visibility and acknowledgment
    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default='private',
        help_text="Who can view this feedback"
    )
    is_acknowledged = models.BooleanField(
        default=False,
        help_text="Whether employee has acknowledged viewing this feedback"
    )
    acknowledged_at = models.DateTimeField(
        null=True, blank=True,
        help_text="When employee acknowledged the feedback"
    )
    employee_response = models.TextField(
        blank=True,
        help_text="Optional response from the employee"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Manager Feedback"
        verbose_name_plural = "Manager Feedback"
        indexes = [
            models.Index(fields=['manager', 'employee'], name='feedback_ma_manager_3811c3_idx'),
            models.Index(fields=['employee', '-created_at'], name='feedback_ma_employe_3bd0a6_idx'),
            models.Index(fields=['-created_at'], name='feedback_ma_created_a6b021_idx')
        ]
    
    def __str__(self):
        return f"{self.manager.get_full_name()} -> {self.employee.get_full_name()}: {self.subject}"