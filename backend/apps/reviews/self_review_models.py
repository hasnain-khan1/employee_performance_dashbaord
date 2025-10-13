"""
Self-Review models for structured employee self-assessment.
Implements BR-027, BR-028, BR-029, BR-030, BR-031.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import json


class SelfReview(models.Model):
    """
    Comprehensive self-review model with structured sections.
    BR-027: Prerequisites validation (approved goals, peer feedback)
    BR-028: Content length enforcement
    BR-029: Auto-save functionality
    BR-030: Submission locking and audit trail
    BR-031: Evidence linking validation
    """
    
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),      # BR-030: Locked status
        ('under_review', 'Under Review'),
        ('completed', 'Completed'),
    ]
    
    # Basic information
    employee = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='self_reviews',
        help_text='Employee completing self-review'
    )
    
    cycle = models.ForeignKey(
        'cycles.ReviewCycle',
        on_delete=models.CASCADE,
        related_name='self_reviews',
        help_text='Review cycle this self-review belongs to'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='not_started',
        help_text='Current status of self-review'
    )
    
    # Section 1: Goal Achievement Summary (150-500 words per goal)
    goal_achievements = models.JSONField(
        default=dict,
        help_text='Goal achievement analysis per approved goal. Format: {goal_id: {text, word_count, evidence_links}}'
    )
    
    # Section 2: Key Accomplishments (200-800 words total)
    key_accomplishments = models.TextField(
        blank=True,
        help_text='Notable achievements and impact during review period (200-800 words)'
    )
    
    key_accomplishments_word_count = models.PositiveIntegerField(
        default=0,
        help_text='Word count for key accomplishments'
    )
    
    recognition_received = models.TextField(
        blank=True,
        help_text='Awards, feedback, or acknowledgments received'
    )
    
    # Section 3: Behavioral Competencies (100-300 words per competency)
    competency_assessments = models.JSONField(
        default=dict,
        help_text='Self-assessment for each competency. Format: {competency_id: {rating, text, word_count, examples}}'
    )
    
    # Section 4: Development Areas (200-600 words)
    development_areas = models.TextField(
        blank=True,
        help_text='Growth opportunities and areas for improvement (200-600 words)'
    )
    
    development_areas_word_count = models.PositiveIntegerField(
        default=0,
        help_text='Word count for development areas'
    )
    
    learning_initiatives = models.TextField(
        blank=True,
        help_text='Training, courses, or development activities completed'
    )
    
    skill_gaps = models.TextField(
        blank=True,
        help_text='Honest assessment of skills needing development'
    )
    
    # Section 5: Career Aspirations (150-400 words)
    career_aspirations = models.TextField(
        blank=True,
        help_text='Professional objectives for next 1-3 years (150-400 words)'
    )
    
    career_aspirations_word_count = models.PositiveIntegerField(
        default=0,
        help_text='Word count for career aspirations'
    )
    
    role_interests = models.TextField(
        blank=True,
        help_text='Desired career progression or lateral moves'
    )
    
    skill_development_goals = models.TextField(
        blank=True,
        help_text='Capabilities employee wants to build'
    )
    
    # BR-031: Evidence Linking
    goal_references = models.JSONField(
        default=list,
        help_text='List of goal IDs referenced in self-review'
    )
    
    feedback_references = models.JSONField(
        default=list,
        help_text='List of peer feedback IDs referenced'
    )
    
    document_attachments = models.JSONField(
        default=list,
        help_text='List of attached documents with URLs'
    )
    
    # BR-029: Auto-save tracking
    last_auto_save = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timestamp of last auto-save'
    )
    
    auto_save_count = models.PositiveIntegerField(
        default=0,
        help_text='Number of auto-saves performed'
    )
    
    last_manual_save = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timestamp of last manual save'
    )
    
    # BR-030: Audit trail metadata
    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When self-review was submitted (BR-030)'
    )
    
    submitted_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='submitted_self_reviews',
        help_text='User who submitted (should match employee)'
    )
    
    submission_version = models.PositiveIntegerField(
        default=1,
        help_text='Version number at submission'
    )
    
    submission_hash = models.CharField(
        max_length=64,
        blank=True,
        help_text='Hash of submitted content for integrity verification'
    )
    
    is_locked = models.BooleanField(
        default=False,
        help_text='Whether self-review is locked after submission (BR-030)'
    )
    
    # Section completion tracking
    section_completion = models.JSONField(
        default=dict,
        help_text='Completion status for each section'
    )
    
    overall_completion_percentage = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Overall completion percentage'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Meta options for SelfReview model."""
        verbose_name = 'Self Review'
        verbose_name_plural = 'Self Reviews'
        ordering = ['-created_at']
        unique_together = ['employee', 'cycle']
    
    def __str__(self):
        """String representation of the self-review."""
        return f"Self Review for {self.employee.employee_id} - {self.cycle.name}"
    
    def clean(self):
        """
        Validate self-review data.
        BR-027: Prerequisites validation
        BR-028: Content length enforcement
        """
        super().clean()
        
        # BR-027: Prerequisites validation
        if self.status in ['submitted', 'under_review', 'completed']:
            self._validate_prerequisites()
        
        # BR-028: Content length validation
        if self.status in ['submitted', 'under_review', 'completed']:
            self._validate_word_limits()
    
    def _validate_prerequisites(self):
        """
        BR-027: Validate prerequisites before submission.
        - Approved goals required
        - Minimum peer feedback responses required
        """
        from apps.goals.models import Goal
        from apps.feedback.models import FeedbackRequest
        
        errors = {}
        
        # Check for approved goals
        approved_goals = Goal.objects.filter(
            employee=self.employee,
            cycle=self.cycle,
            status='approved'
        )
        
        if not approved_goals.exists():
            errors['prerequisites'] = [
                'You must have at least one approved goal before submitting your self-review. '
                'Please ensure your manager has approved your goals.'
            ]
        
        # Check for peer feedback responses
        feedback_requests = FeedbackRequest.objects.filter(
            requester=self.employee,
            cycle=self.cycle,
            status='completed'
        )
        
        # Get minimum required feedback from cycle config
        min_feedback = getattr(self.cycle, 'min_peer_feedback', 1)
        completed_count = feedback_requests.count()
        
        if completed_count < min_feedback:
            if 'prerequisites' not in errors:
                errors['prerequisites'] = []
            errors['prerequisites'].append(
                f'You must have at least {min_feedback} completed peer feedback response(s) before submitting. '
                f'Currently you have {completed_count}. Please wait for peer responses or request additional feedback.'
            )
        
        if errors:
            raise ValidationError(errors)
    
    def _validate_word_limits(self):
        """
        BR-028: Validate word count limits for each section.
        """
        errors = {}
        
        # Section 2: Key Accomplishments (200-800 words)
        if self.key_accomplishments:
            word_count = len(self.key_accomplishments.split())
            if word_count < 200:
                errors['key_accomplishments'] = f'Key accomplishments must be at least 200 words (currently {word_count} words).'
            elif word_count > 800:
                errors['key_accomplishments'] = f'Key accomplishments cannot exceed 800 words (currently {word_count} words). Please condense your content.'
        else:
            errors['key_accomplishments'] = 'Key accomplishments section is required.'
        
        # Section 4: Development Areas (200-600 words)
        if self.development_areas:
            word_count = len(self.development_areas.split())
            if word_count < 200:
                errors['development_areas'] = f'Development areas must be at least 200 words (currently {word_count} words).'
            elif word_count > 600:
                errors['development_areas'] = f'Development areas cannot exceed 600 words (currently {word_count} words). Please condense your content.'
        else:
            errors['development_areas'] = 'Development areas section is required.'
        
        # Section 5: Career Aspirations (150-400 words)
        if self.career_aspirations:
            word_count = len(self.career_aspirations.split())
            if word_count < 150:
                errors['career_aspirations'] = f'Career aspirations must be at least 150 words (currently {word_count} words).'
            elif word_count > 400:
                errors['career_aspirations'] = f'Career aspirations cannot exceed 400 words (currently {word_count} words). Please condense your content.'
        else:
            errors['career_aspirations'] = 'Career aspirations section is required.'
        
        # Section 1: Goal achievements (150-500 words per goal)
        if not self.goal_achievements:
            errors['goal_achievements'] = 'Goal achievement analysis is required for all approved goals.'
        else:
            for goal_id, achievement_data in self.goal_achievements.items():
                text = achievement_data.get('text', '')
                word_count = len(text.split())
                if word_count < 150:
                    errors[f'goal_achievement_{goal_id}'] = f'Goal {goal_id} analysis must be at least 150 words (currently {word_count} words).'
                elif word_count > 500:
                    errors[f'goal_achievement_{goal_id}'] = f'Goal {goal_id} analysis cannot exceed 500 words (currently {word_count} words).'
        
        # Section 3: Competency assessments (100-300 words per competency)
        if not self.competency_assessments:
            errors['competency_assessments'] = 'Competency self-assessment is required.'
        else:
            for comp_id, comp_data in self.competency_assessments.items():
                text = comp_data.get('text', '')
                word_count = len(text.split())
                if word_count < 100:
                    errors[f'competency_{comp_id}'] = f'Competency {comp_id} assessment must be at least 100 words (currently {word_count} words).'
                elif word_count > 300:
                    errors[f'competency_{comp_id}'] = f'Competency {comp_id} assessment cannot exceed 300 words (currently {word_count} words).'
        
        if errors:
            raise ValidationError(errors)
    
    def auto_save(self):
        """
        BR-029: Perform auto-save without triggering full validation.
        Called every 30 seconds by frontend.
        """
        self.last_auto_save = timezone.now()
        self.auto_save_count += 1
        # Save without calling clean() to avoid validation errors during drafting
        super(SelfReview, self).save(update_fields=[
            'goal_achievements', 'key_accomplishments', 'key_accomplishments_word_count',
            'recognition_received', 'competency_assessments', 'development_areas',
            'development_areas_word_count', 'learning_initiatives', 'skill_gaps',
            'career_aspirations', 'career_aspirations_word_count', 'role_interests',
            'skill_development_goals', 'goal_references', 'feedback_references',
            'document_attachments', 'last_auto_save', 'auto_save_count',
            'section_completion', 'overall_completion_percentage', 'updated_at'
        ])
    
    def manual_save(self):
        """Manual save with partial validation."""
        self.last_manual_save = timezone.now()
        self.save()
    
    def submit(self, user):
        """
        BR-030: Submit self-review with locking and audit trail.
        Creates immutable audit trail metadata.
        """
        import hashlib
        
        # Validate prerequisites and content
        self.full_clean()
        
        # Set submission metadata
        self.status = 'submitted'
        self.submitted_at = timezone.now()
        self.submitted_by = user
        self.is_locked = True
        
        # Increment version
        self.submission_version += 1
        
        # Create content hash for integrity
        content_data = {
            'goal_achievements': self.goal_achievements,
            'key_accomplishments': self.key_accomplishments,
            'competency_assessments': self.competency_assessments,
            'development_areas': self.development_areas,
            'career_aspirations': self.career_aspirations,
        }
        content_str = json.dumps(content_data, sort_keys=True)
        self.submission_hash = hashlib.sha256(content_str.encode()).hexdigest()
        
        self.save()
        
        # Create audit trail version
        SelfReviewVersion.objects.create(
            self_review=self,
            version_number=self.submission_version,
            content_snapshot=content_data,
            changed_by=user,
            change_type='submitted',
            change_summary='Self-review submitted for manager evaluation'
        )
    
    def validate_evidence_links(self):
        """
        BR-031: Validate that referenced goals and feedback exist.
        """
        from apps.goals.models import Goal
        from apps.feedback.models import FeedbackRequest
        
        errors = {}
        
        # Validate goal references
        if self.goal_references:
            valid_goals = Goal.objects.filter(
                id__in=self.goal_references,
                employee=self.employee,
                cycle=self.cycle
            ).values_list('id', flat=True)
            
            invalid_goals = set(self.goal_references) - set(valid_goals)
            if invalid_goals:
                errors['goal_references'] = f'Invalid goal references: {invalid_goals}'
        
        # Validate feedback references
        if self.feedback_references:
            valid_feedback = FeedbackRequest.objects.filter(
                id__in=self.feedback_references,
                requester=self.employee,
                cycle=self.cycle
            ).values_list('id', flat=True)
            
            invalid_feedback = set(self.feedback_references) - set(valid_feedback)
            if invalid_feedback:
                errors['feedback_references'] = f'Invalid feedback references: {invalid_feedback}'
        
        if errors:
            raise ValidationError(errors)
    
    def calculate_completion_percentage(self):
        """Calculate overall completion percentage."""
        sections = [
            bool(self.goal_achievements),
            bool(self.key_accomplishments and len(self.key_accomplishments.split()) >= 200),
            bool(self.competency_assessments),
            bool(self.development_areas and len(self.development_areas.split()) >= 200),
            bool(self.career_aspirations and len(self.career_aspirations.split()) >= 150),
        ]
        
        completed = sum(sections)
        total = len(sections)
        
        self.overall_completion_percentage = int((completed / total) * 100)
        return self.overall_completion_percentage


class SelfReviewVersion(models.Model):
    """
    Version history for self-reviews.
    BR-030: Maintains audit trail of all changes.
    """
    
    self_review = models.ForeignKey(
        SelfReview,
        on_delete=models.CASCADE,
        related_name='versions',
        help_text='Self-review this version belongs to'
    )
    
    version_number = models.PositiveIntegerField(
        help_text='Version number'
    )
    
    content_snapshot = models.JSONField(
        help_text='Complete snapshot of self-review content'
    )
    
    changed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='self_review_versions',
        help_text='User who made the change'
    )
    
    change_type = models.CharField(
        max_length=20,
        choices=[
            ('created', 'Created'),
            ('auto_saved', 'Auto Saved'),
            ('manually_saved', 'Manually Saved'),
            ('submitted', 'Submitted'),
            ('reopened', 'Reopened'),
        ],
        help_text='Type of change'
    )
    
    change_summary = models.TextField(
        blank=True,
        help_text='Summary of changes made'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        """Meta options for SelfReviewVersion model."""
        verbose_name = 'Self Review Version'
        verbose_name_plural = 'Self Review Versions'
        ordering = ['-version_number', '-created_at']
        unique_together = ['self_review', 'version_number']
    
    def __str__(self):
        """String representation of the version."""
        return f"Self Review v{self.version_number} - {self.self_review.employee.employee_id}"


class SelfReviewAttachment(models.Model):
    """
    Attachments for self-reviews (supporting evidence).
    """
    
    self_review = models.ForeignKey(
        SelfReview,
        on_delete=models.CASCADE,
        related_name='attachments',
        help_text='Self-review this attachment belongs to'
    )
    
    file_name = models.CharField(
        max_length=255,
        help_text='Original file name'
    )
    
    file_url = models.URLField(
        help_text='URL to the file (S3, cloud storage, etc.)'
    )
    
    file_type = models.CharField(
        max_length=50,
        help_text='MIME type of the file'
    )
    
    file_size = models.PositiveIntegerField(
        help_text='File size in bytes'
    )
    
    description = models.TextField(
        blank=True,
        help_text='Description of the attachment'
    )
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        """Meta options for SelfReviewAttachment model."""
        verbose_name = 'Self Review Attachment'
        verbose_name_plural = 'Self Review Attachments'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        """String representation of the attachment."""
        return f"{self.file_name} - {self.self_review}"

