"""
Feedback models for the EPMS system.

This module contains models for peer feedback management,
including feedback requests, responses, and evaluation.
Also includes manager-to-employee continuous feedback.
Implements BR-022, BR-023, BR-024, BR-025, BR-026.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import re


class FeedbackRequest(models.Model):
    """
    Feedback request model for peer feedback.
    BR-022: Peer feedback requests limited to 1-5 reviewers per employee.
    BR-024: Automated reminder system with manager escalation.
    BR-025: Feedback window closes automatically at configured deadline.
    
    Represents a request for feedback from one employee
    to another during a review cycle.
    """
    
    # Status choices
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),  # BR-025: Auto-expired at deadline
    ]
    
    # Relationship type choices
    RELATIONSHIP_CHOICES = [
        ('direct_report', 'Direct Report'),
        ('peer_same_team', 'Peer - Same Team'),
        ('peer_other_team', 'Peer - Other Team'),
        ('cross_functional', 'Cross-Functional Collaborator'),
        ('project_team', 'Project Team Member'),
        ('mentor_mentee', 'Mentor/Mentee'),
        ('other', 'Other'),
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
    
    relationship_type = models.CharField(
        max_length=30,
        choices=RELATIONSHIP_CHOICES,
        default='peer_other_team',
        help_text='Working relationship context'
    )
    
    relationship_description = models.TextField(
        blank=True,
        help_text='Optional description of working relationship'
    )
    
    message = models.TextField(
        help_text='Personalized message from the requester'
    )
    
    due_date = models.DateTimeField(
        help_text='Due date for the feedback (BR-025)'
    )
    
    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the feedback was submitted'
    )
    
    # BR-024: Reminder tracking
    reminder_count = models.PositiveIntegerField(
        default=0,
        help_text='Number of reminders sent'
    )
    
    last_reminder_sent = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the last reminder was sent'
    )
    
    manager_notified = models.BooleanField(
        default=False,
        help_text='Whether manager has been notified of non-response (BR-024)'
    )
    
    manager_notified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When manager was notified'
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
    
    def clean(self):
        """
        Validate feedback request.
        BR-022: Peer feedback requests limited to 1-5 reviewers per employee.
        """
        super().clean()
        
        # BR-022: Validate peer count (1-5 reviewers)
        if not self.pk:  # Only for new requests
            existing_requests = FeedbackRequest.objects.filter(
                requester=self.requester,
                cycle=self.cycle
            ).exclude(status__in=['declined', 'expired']).count()
            
            # Get max peer feedback from cycle configuration
            max_peers = getattr(self.cycle, 'max_peer_feedback', 5)
            
            if existing_requests >= max_peers:
                raise ValidationError({
                    'non_field_errors': f'You can only request feedback from up to {max_peers} peers per cycle. '
                                       f'You currently have {existing_requests} active requests. '
                                       f'Please wait for responses or cancel existing requests.'
                })
            
            if existing_requests < 1 and max_peers < 1:
                raise ValidationError({
                    'non_field_errors': 'At least 1 peer reviewer is required for this cycle.'
                })
        
        # Validate due date is in the future
        if self.due_date and self.due_date < timezone.now():
            raise ValidationError({
                'due_date': 'Due date must be in the future.'
            })
        
        # Prevent self-feedback
        if self.requester == self.recipient:
            raise ValidationError({
                'recipient': 'You cannot request feedback from yourself.'
            })
    
    @property
    def is_overdue(self):
        """Check if feedback request is overdue (BR-025)."""
        return self.status == 'pending' and timezone.now() > self.due_date
    
    @property
    def days_until_due(self):
        """Get days remaining until due date."""
        if self.status == 'completed':
            return 0
        delta = self.due_date - timezone.now()
        return max(0, delta.days)
    
    def should_send_reminder(self):
        """
        Check if reminder should be sent (BR-024).
        Reminders at Day 7, 14, 21 after request.
        """
        if self.status != 'pending':
            return False
        
        days_since_request = (timezone.now() - self.created_at).days
        reminder_days = [7, 14, 21]
        
        # Check if we should send next reminder
        if self.reminder_count < len(reminder_days):
            target_day = reminder_days[self.reminder_count]
            if days_since_request >= target_day:
                # Check if we haven't sent a reminder today
                if not self.last_reminder_sent or \
                   (timezone.now() - self.last_reminder_sent).days >= 1:
                    return True
        
        return False
    
    def should_notify_manager(self):
        """
        Check if manager should be notified (BR-024).
        Manager escalation at Day 25.
        """
        if self.status != 'pending' or self.manager_notified:
            return False
        
        days_since_request = (timezone.now() - self.created_at).days
        return days_since_request >= 25
    
    def mark_expired(self):
        """Mark request as expired if past due date (BR-025)."""
        if self.status == 'pending' and timezone.now() > self.due_date:
            self.status = 'expired'
            self.save()
            return True
        return False


class ContentPolicyValidator:
    """
    Content policy validator for feedback text.
    BR-023: Content policy enforcement blocks submission of inappropriate language.
    """
    
    # Profanity word list (customizable by HR)
    PROFANITY_WORDS = [
        'damn', 'hell', 'crap', 'stupid', 'idiot', 'fool', 'incompetent',
        'lazy', 'useless', 'worthless', 'terrible', 'awful', 'horrible',
        # Add more words as needed
    ]
    
    # Bias-indicating phrases
    BIAS_PHRASES = [
        'too old', 'too young', 'for a woman', 'for a man', 'for his age',
        'for her age', 'not technical enough', 'too emotional', 'too aggressive'
    ]
    
    # Minimum word counts for substantive feedback
    MIN_WORD_COUNTS = {
        'strengths': 20,  # ~100 characters
        'areas_for_improvement': 20,
        'specific_examples': 15,
    }
    
    @classmethod
    def validate_text(cls, text, field_name='feedback'):
        """
        Validate text against content policy.
        Returns tuple: (is_valid, error_messages)
        """
        errors = []
        text_lower = text.lower()
        
        # Check for profanity
        found_profanity = []
        for word in cls.PROFANITY_WORDS:
            if re.search(r'\b' + word + r'\b', text_lower):
                found_profanity.append(word)
        
        if found_profanity:
            errors.append(
                f"Please use professional language. Found inappropriate words: {', '.join(found_profanity)}. "
                "Consider rephrasing to maintain a constructive tone."
            )
        
        # Check for bias
        found_bias = []
        for phrase in cls.BIAS_PHRASES:
            if phrase in text_lower:
                found_bias.append(phrase)
        
        if found_bias:
            errors.append(
                f"Potential bias detected. Please review phrases: {', '.join(found_bias)}. "
                "Focus on behaviors and specific examples rather than personal characteristics."
            )
        
        # Check minimum length
        if field_name in cls.MIN_WORD_COUNTS:
            word_count = len(text.split())
            min_words = cls.MIN_WORD_COUNTS[field_name]
            if word_count < min_words:
                errors.append(
                    f"Please provide more detailed feedback. "
                    f"Minimum {min_words} words required (currently {word_count} words)."
                )
        
        # Check for overly negative tone (all caps, excessive exclamation)
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if caps_ratio > 0.5:
            errors.append(
                "Please avoid using excessive capital letters. "
                "Feedback should be constructive and professional."
            )
        
        exclamation_count = text.count('!')
        if exclamation_count > 3:
            errors.append(
                "Please use a more measured tone. "
                "Reduce the use of exclamation marks for professional feedback."
            )
        
        return len(errors) == 0, errors
    
    @classmethod
    def validate_all_fields(cls, strengths, areas_for_improvement, specific_examples, recommendations=''):
        """Validate all feedback fields at once."""
        all_errors = {}
        
        valid, errors = cls.validate_text(strengths, 'strengths')
        if not valid:
            all_errors['strengths'] = errors
        
        valid, errors = cls.validate_text(areas_for_improvement, 'areas_for_improvement')
        if not valid:
            all_errors['areas_for_improvement'] = errors
        
        valid, errors = cls.validate_text(specific_examples, 'specific_examples')
        if not valid:
            all_errors['specific_examples'] = errors
        
        if recommendations:
            valid, errors = cls.validate_text(recommendations, 'recommendations')
            if not valid:
                all_errors['recommendations'] = errors
        
        return len(all_errors) == 0, all_errors


class FeedbackResponse(models.Model):
    """
    Feedback response model.
    BR-023: Content policy enforcement blocks submission of inappropriate language.
    BR-026: Anonymous feedback cannot be attributed to individual reviewers.
    
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
    
    # Behavioral competencies ratings (JSON field for flexibility)
    competency_ratings = models.JSONField(
        default=dict,
        help_text='Ratings for behavioral competencies'
    )
    
    # Detailed feedback
    strengths = models.TextField(
        help_text='Strengths and positive aspects (min 20 words)'
    )
    
    areas_for_improvement = models.TextField(
        help_text='Areas for improvement (min 20 words)'
    )
    
    specific_examples = models.TextField(
        help_text='Specific examples of collaboration (min 15 words)'
    )
    
    recommendations = models.TextField(
        help_text='Recommendations for development'
    )
    
    # Additional comments
    additional_comments = models.TextField(
        blank=True,
        help_text='Any additional comments'
    )
    
    # BR-026: Anonymity controls
    is_anonymous = models.BooleanField(
        default=False,
        help_text='Whether the feedback is anonymous (BR-026)'
    )
    
    # Draft capability
    is_draft = models.BooleanField(
        default=True,
        help_text='Whether this is a draft (allows partial save)'
    )
    
    # BR-023: Content policy validation tracking
    content_policy_passed = models.BooleanField(
        default=False,
        help_text='Whether content passed policy validation (BR-023)'
    )
    
    validation_issues = models.JSONField(
        default=dict,
        blank=True,
        help_text='Content policy validation issues detected'
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
        status = "Anonymous" if self.is_anonymous else "Named"
        return f"{status} Response for {self.request}"
    
    def clean(self):
        """
        Validate feedback response.
        BR-023: Content policy enforcement.
        """
        super().clean()
        
        # BR-023: Content policy validation (only for non-draft)
        if not self.is_draft:
            is_valid, errors = ContentPolicyValidator.validate_all_fields(
                self.strengths,
                self.areas_for_improvement,
                self.specific_examples,
                self.recommendations
            )
            
            if not is_valid:
                self.content_policy_passed = False
                self.validation_issues = errors
                # Raise validation error with all issues
                error_messages = []
                for field, field_errors in errors.items():
                    error_messages.append(f"{field}: " + " ".join(field_errors))
                
                raise ValidationError({
                    'non_field_errors': 'Content policy violations detected. Please review and correct the following:\n' + 
                                       '\n'.join(error_messages)
                })
            else:
                self.content_policy_passed = True
                self.validation_issues = {}
    
    def save(self, *args, **kwargs):
        """Override save to update request status."""
        # If submitting (not draft), update request status
        if not self.is_draft and self.request.status == 'pending':
            self.request.status = 'completed'
            self.request.submitted_at = timezone.now()
            self.request.save()
        
        super().save(*args, **kwargs)


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


class ManagerFeedback(models.Model):
    """
    Manager-to-Employee continuous feedback model.
    
    Allows managers to provide ongoing feedback to their direct reports,
    separate from formal peer feedback and performance reviews.
    """
    
    # Feedback type choices
    TYPE_CHOICES = [
        ('recognition', 'Recognition'),
        ('constructive', 'Constructive'),
        ('coaching', 'Coaching'),
        ('development', 'Development'),
        ('general', 'General'),
    ]
    
    # Visibility choices
    VISIBILITY_CHOICES = [
        ('private', 'Private (Manager & Employee only)'),
        ('hr', 'Visible to HR'),
        ('public', 'Public (Visible to all)'),
    ]
    
    manager = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='manager_feedback_given',
        help_text='Manager providing the feedback'
    )
    
    employee = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='manager_feedback_received',
        help_text='Employee receiving the feedback'
    )
    
    cycle = models.ForeignKey(
        'cycles.ReviewCycle',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='manager_feedback',
        help_text='Optional: Associated review cycle'
    )
    
    feedback_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='general',
        help_text='Type of feedback'
    )
    
    subject = models.CharField(
        max_length=200,
        help_text='Brief subject/title of the feedback'
    )
    
    feedback = models.TextField(
        help_text='Detailed feedback content'
    )
    
    strengths = models.TextField(
        blank=True,
        help_text='Specific strengths observed (optional)'
    )
    
    areas_for_improvement = models.TextField(
        blank=True,
        help_text='Areas for growth and development (optional)'
    )
    
    action_items = models.TextField(
        blank=True,
        help_text='Suggested action items or next steps (optional)'
    )
    
    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default='private',
        help_text='Who can view this feedback'
    )
    
    is_acknowledged = models.BooleanField(
        default=False,
        help_text='Whether employee has acknowledged viewing this feedback'
    )
    
    acknowledged_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When employee acknowledged the feedback'
    )
    
    employee_response = models.TextField(
        blank=True,
        help_text='Optional response from the employee'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Meta options for ManagerFeedback model."""
        verbose_name = 'Manager Feedback'
        verbose_name_plural = 'Manager Feedback'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['manager', 'employee']),
            models.Index(fields=['employee', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        """String representation of the manager feedback."""
        return f"{self.manager.get_full_name()} → {self.employee.get_full_name()}: {self.subject}"
    
    def clean(self):
        """Validate manager feedback."""
        super().clean()
        
        # Validate that manager is actually the employee's manager
        if self.employee.manager != self.manager:
            raise ValidationError({
                'manager': 'You can only provide feedback to your direct reports.'
            })
    
    def save(self, *args, **kwargs):
        """Override save to run validation."""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def acknowledge(self, response=None):
        """Mark feedback as acknowledged by employee."""
        self.is_acknowledged = True
        self.acknowledged_at = timezone.now()
        if response:
            self.employee_response = response
        self.save()