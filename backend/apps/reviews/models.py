"""
Models for the reviews app.

This module contains models for self-review and manager review management,
including structured content, evidence linking, and audit trails.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.conf import settings

User = get_user_model()


class SelfReview(models.Model):
    """
    Model representing an employee's self-review.
    """
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('completed', 'Completed'),
        ('returned', 'Returned for Revision')
    ]
    
    # Review details
    employee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='self_reviews',
        help_text="Employee completing the self-review"
    )
    cycle = models.ForeignKey(
        'cycles.ReviewCycle',
        on_delete=models.CASCADE,
        related_name='self_reviews',
        help_text="Performance cycle for this review"
    )
    
    # Review content sections
    goal_achievement_summary = models.TextField(
        blank=True,
        help_text="Summary of goal achievements with evidence"
    )
    key_accomplishments = models.TextField(
        blank=True,
        help_text="Notable achievements and contributions"
    )
    behavioral_competencies = models.TextField(
        blank=True,
        help_text="Self-assessment of behavioral competencies"
    )
    development_areas = models.TextField(
        blank=True,
        help_text="Areas for growth and development"
    )
    career_aspirations = models.TextField(
        blank=True,
        help_text="Future goals and career objectives"
    )
    
    # Status and tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text="Current status of the self-review"
    )
    completion_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage of review completion"
    )
    
    # Audit trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    last_auto_save = models.DateTimeField(null=True, blank=True)
    
    # Prerequisites tracking
    goals_approved = models.BooleanField(default=False)
    peer_feedback_received = models.BooleanField(default=False)
    prerequisites_met = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['employee', 'cycle']
        ordering = ['-created_at']
        verbose_name = "Self Review"
        verbose_name_plural = "Self Reviews"
    
    def __str__(self):
        return f"Self Review: {self.employee.get_full_name()} - {self.cycle.name}"
    
    def save(self, *args, **kwargs):
        """Calculate completion percentage on save."""
        self.calculate_completion_percentage()
        super().save(*args, **kwargs)
    
    def calculate_completion_percentage(self):
        """Calculate completion percentage based on filled sections."""
        sections = [
            self.goal_achievement_summary,
            self.key_accomplishments,
            self.behavioral_competencies,
            self.development_areas,
            self.career_aspirations
        ]
        
        filled_sections = sum(1 for section in sections if section.strip())
        self.completion_percentage = (filled_sections / len(sections)) * 100


class ManagerReview(models.Model):
    """
    Model representing a manager's final review and rating of an employee.
    """
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('returned', 'Returned for Revision')
    ]
    
    # Review details
    employee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='manager_reviews_received',
        help_text="Employee being reviewed"
    )
    manager = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='manager_reviews_given',
        help_text="Manager conducting the review"
    )
    cycle = models.ForeignKey(
        'cycles.ReviewCycle',
        on_delete=models.CASCADE,
        related_name='manager_reviews',
        help_text="Performance cycle for this review"
    )
    
    # Review period
    review_period_start = models.DateField(
        help_text="Start date of the review period"
    )
    review_period_end = models.DateField(
        help_text="End date of the review period"
    )
    
    # Goals and achievements
    goals_achievements = models.TextField(
        blank=True,
        help_text="Manager's assessment of goal achievements"
    )
    
    # Competency ratings
    communication_rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Communication skills rating (1-5)"
    )
    collaboration_rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Collaboration skills rating (1-5)"
    )
    leadership_rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Leadership skills rating (1-5)"
    )
    problem_solving_rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Problem-solving skills rating (1-5)"
    )
    adaptability_rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Adaptability rating (1-5)"
    )
    
    # Overall rating
    overall_rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Overall performance rating (1-5)"
    )
    
    # Narrative sections
    performance_summary = models.TextField(
        blank=True,
        help_text="Manager's performance summary narrative"
    )
    strengths = models.TextField(
        blank=True,
        help_text="Employee's key strengths"
    )
    development_areas = models.TextField(
        blank=True,
        help_text="Areas for development and improvement"
    )
    career_recommendations = models.TextField(
        blank=True,
        help_text="Career development recommendations"
    )
    
    # Additional fields
    comments = models.TextField(
        blank=True,
        help_text="Additional comments (max 5000 characters)"
    )
    private_notes = models.TextField(
        blank=True,
        help_text="Private manager notes (not visible to employee)"
    )
    development_notes = models.TextField(
        blank=True,
        help_text="Development planning notes"
    )
    
    # Status and tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text="Current status of the review"
    )
    is_locked = models.BooleanField(
        default=False,
        help_text="Whether the review is locked from editing"
    )
    
    # Audit trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    last_auto_save = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['employee', 'cycle', 'manager']
        ordering = ['-created_at']
        verbose_name = "Manager Review"
        verbose_name_plural = "Manager Reviews"
    
    def __str__(self):
        return f"Manager Review: {self.employee.get_full_name()} by {self.manager.get_full_name()}"
    
    @property
    def average_competency_rating(self):
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
    
    @property
    def is_complete(self):
        """Check if all required sections are completed."""
        required_sections = [
            self.performance_summary,
            self.strengths,
            self.development_areas,
            self.career_recommendations
        ]
        return all(section.strip() for section in required_sections) and self.overall_rating is not None


class ReviewAttachment(models.Model):
    """
    Model for review attachments.
    """
    
    ATTACHMENT_TYPES = [
        ('document', 'Document'),
        ('image', 'Image'),
        ('spreadsheet', 'Spreadsheet'),
        ('presentation', 'Presentation'),
        ('other', 'Other')
    ]
    
    # Relationships
    manager_review = models.ForeignKey(
        ManagerReview,
        on_delete=models.CASCADE,
        related_name='attachments',
        help_text="The manager review this attachment belongs to"
    )
    
    # Attachment details
    file = models.FileField(
        upload_to='review_attachments/',
        help_text="Uploaded file"
    )
    file_name = models.CharField(
        max_length=255,
        help_text="Original file name"
    )
    file_size = models.BigIntegerField(
        help_text="File size in bytes"
    )
    file_type = models.CharField(
        max_length=50,
        choices=ATTACHMENT_TYPES,
        help_text="Type of attachment"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the attachment"
    )
    
    # Metadata
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='review_attachments_uploaded'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Review Attachment"
        verbose_name_plural = "Review Attachments"
    
    def __str__(self):
        return f"{self.file_name} - {self.manager_review.employee.get_full_name()}"


class ReviewAuditTrail(models.Model):
    """
    Model for tracking changes to reviews.
    """
    
    ACTION_TYPES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('returned', 'Returned'),
        ('locked', 'Locked'),
        ('unlocked', 'Unlocked')
    ]
    
    # Relationships
    manager_review = models.ForeignKey(
        ManagerReview,
        on_delete=models.CASCADE,
        related_name='audit_trail',
        help_text="The manager review this audit entry belongs to"
    )
    
    # Audit details
    action = models.CharField(
        max_length=20,
        choices=ACTION_TYPES,
        help_text="Type of action performed"
    )
    field_changed = models.CharField(
        max_length=50,
        blank=True,
        help_text="Field that was changed"
    )
    old_value = models.TextField(
        blank=True,
        help_text="Previous value"
    )
    new_value = models.TextField(
        blank=True,
        help_text="New value"
    )
    change_summary = models.TextField(
        blank=True,
        help_text="Summary of changes made"
    )
    
    # Metadata
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='review_audit_actions',
        help_text="User who performed the action"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(
        null=True, blank=True,
        help_text="IP address of the user"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="User agent string"
    )
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Review Audit Trail"
        verbose_name_plural = "Review Audit Trails"
    
    def __str__(self):
        return f"{self.action}: {self.manager_review.employee.get_full_name()} - {self.timestamp}"


class SelfReviewSection(models.Model):
    """
    Model representing individual sections of a self-review.
    """
    
    SECTION_TYPES = [
        ('goal_achievement', 'Goal Achievement Summary'),
        ('accomplishments', 'Key Accomplishments'),
        ('competencies', 'Behavioral Competencies'),
        ('development', 'Development Areas'),
        ('career', 'Career Aspirations')
    ]
    
    # Relationships
    self_review = models.ForeignKey(
        SelfReview,
        on_delete=models.CASCADE,
        related_name='sections',
        help_text="The self-review this section belongs to"
    )
    
    # Section details
    section_type = models.CharField(
        max_length=20,
        choices=SECTION_TYPES,
        help_text="Type of section"
    )
    content = models.TextField(
        blank=True,
        help_text="Section content"
    )
    word_count = models.IntegerField(
        default=0,
        help_text="Current word count"
    )
    is_completed = models.BooleanField(
        default=False,
        help_text="Whether section is marked as completed"
    )
    
    # Word limits
    min_words = models.IntegerField(
        default=0,
        help_text="Minimum word count required"
    )
    max_words = models.IntegerField(
        default=1000,
        help_text="Maximum word count allowed"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['self_review', 'section_type']
        ordering = ['section_type']
        verbose_name = "Self Review Section"
        verbose_name_plural = "Self Review Sections"
    
    def __str__(self):
        return f"{self.get_section_type_display()} - {self.self_review.employee.get_full_name()}"
    
    def save(self, *args, **kwargs):
        """Calculate word count on save."""
        self.word_count = len(self.content.split()) if self.content else 0
        super().save(*args, **kwargs)


class EvidenceLink(models.Model):
    """
    Model representing evidence links in self-reviews.
    """
    
    LINK_TYPES = [
        ('goal', 'Goal Reference'),
        ('feedback', 'Peer Feedback'),
        ('document', 'Document Attachment'),
        ('url', 'URL Link'),
        ('metric', 'Performance Metric')
    ]
    
    # Relationships
    self_review = models.ForeignKey(
        SelfReview,
        on_delete=models.CASCADE,
        related_name='evidence_links',
        help_text="The self-review this evidence belongs to"
    )
    section = models.ForeignKey(
        SelfReviewSection,
        on_delete=models.CASCADE,
        related_name='evidence_links',
        null=True, blank=True,
        help_text="Specific section this evidence relates to"
    )
    
    # Link details
    link_type = models.CharField(
        max_length=20,
        choices=LINK_TYPES,
        help_text="Type of evidence link"
    )
    title = models.CharField(
        max_length=200,
        help_text="Title or description of the evidence"
    )
    reference_id = models.IntegerField(
        null=True, blank=True,
        help_text="ID of referenced goal or feedback"
    )
    url = models.URLField(
        blank=True,
        help_text="URL link if applicable"
    )
    file_attachment = models.FileField(
        upload_to='self_review_evidence/',
        null=True, blank=True,
        help_text="File attachment if applicable"
    )
    description = models.TextField(
        blank=True,
        help_text="Additional description of the evidence"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Evidence Link"
        verbose_name_plural = "Evidence Links"
    
    def __str__(self):
        return f"{self.title} - {self.self_review.employee.get_full_name()}"


class SelfReviewDraft(models.Model):
    """
    Model for auto-saved drafts of self-reviews.
    """
    
    # Relationships
    self_review = models.ForeignKey(
        SelfReview,
        on_delete=models.CASCADE,
        related_name='drafts',
        help_text="The self-review this draft belongs to"
    )
    
    # Draft content
    section_type = models.CharField(
        max_length=20,
        help_text="Type of section being drafted"
    )
    content = models.TextField(
        help_text="Draft content"
    )
    word_count = models.IntegerField(
        default=0,
        help_text="Word count of draft content"
    )
    
    # Auto-save metadata
    is_auto_save = models.BooleanField(
        default=True,
        help_text="Whether this is an automatic save"
    )
    save_reason = models.CharField(
        max_length=50,
        default='auto_save',
        help_text="Reason for saving (auto_save, manual_save, etc.)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Self Review Draft"
        verbose_name_plural = "Self Review Drafts"
    
    def __str__(self):
        return f"Draft: {self.self_review.employee.get_full_name()} - {self.section_type}"


class SelfReviewAuditTrail(models.Model):
    """
    Model for tracking changes to self-reviews.
    """
    
    ACTION_TYPES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('auto_saved', 'Auto-saved'),
        ('submitted', 'Submitted'),
        ('returned', 'Returned'),
        ('completed', 'Completed')
    ]
    
    # Relationships
    self_review = models.ForeignKey(
        SelfReview,
        on_delete=models.CASCADE,
        related_name='audit_trail',
        help_text="The self-review this audit entry belongs to"
    )
    
    # Audit details
    action = models.CharField(
        max_length=20,
        choices=ACTION_TYPES,
        help_text="Type of action performed"
    )
    section_type = models.CharField(
        max_length=20,
        blank=True,
        help_text="Section that was modified"
    )
    changes_summary = models.TextField(
        blank=True,
        help_text="Summary of changes made"
    )
    previous_content = models.TextField(
        blank=True,
        help_text="Previous content before change"
    )
    new_content = models.TextField(
        blank=True,
        help_text="New content after change"
    )
    
    # Metadata
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='self_review_audit_actions',
        help_text="User who performed the action"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(
        null=True, blank=True,
        help_text="IP address of the user"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="User agent string"
    )
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Self Review Audit Trail"
        verbose_name_plural = "Self Review Audit Trails"
    
    def __str__(self):
        return f"{self.action}: {self.self_review.employee.get_full_name()} - {self.timestamp}"


class SelfReviewTemplate(models.Model):
    """
    Model for self-review templates and guidelines.
    """
    
    # Template details
    name = models.CharField(
        max_length=100,
        help_text="Template name"
    )
    description = models.TextField(
        blank=True,
        help_text="Template description"
    )
    
    # Section configurations
    sections_config = models.JSONField(
        default=dict,
        help_text="Configuration for each section including word limits"
    )
    
    # Guidelines
    writing_guidelines = models.TextField(
        blank=True,
        help_text="Writing guidelines and tips"
    )
    examples = models.JSONField(
        default=list,
        help_text="Example responses for each section"
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
        related_name='self_review_templates_created'
    )
    
    class Meta:
        ordering = ['-is_default', 'name']
        verbose_name = "Self Review Template"
        verbose_name_plural = "Self Review Templates"
    
    def __str__(self):
        return self.name