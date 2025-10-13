"""
Review cycle models for the EPMS system.

This module contains models for managing performance review cycles,
including cycle setup, employee participation, and cycle status tracking.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from datetime import date, timedelta


class ReviewCycle(models.Model):
    """
    Review cycle model for performance management.
    
    Represents a performance review cycle with defined periods,
    participants, and evaluation criteria.
    """
    
    # Cycle status choices
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Cycle type choices
    TYPE_CHOICES = [
        ('annual', 'Annual'),
        ('mid_year', 'Mid-Year'),
        ('quarterly', 'Quarterly'),
        ('probation', 'Probation'),
        ('project', 'Project-Based'),
    ]
    
    name = models.CharField(
        max_length=200,
        help_text='Name of the review cycle'
    )
    
    description = models.TextField(
        blank=True,
        help_text='Description of the review cycle'
    )
    
    cycle_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='annual',
        help_text='Type of review cycle'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text='Current status of the cycle'
    )
    
    start_date = models.DateField(
        help_text='Start date of the review cycle'
    )
    
    end_date = models.DateField(
        help_text='End date of the review cycle'
    )
    
    goal_setting_start = models.DateField(
        help_text='Start date for goal setting period'
    )
    
    goal_setting_end = models.DateField(
        help_text='End date for goal setting period'
    )
    
    self_review_start = models.DateField(
        help_text='Start date for self-review period'
    )
    
    self_review_end = models.DateField(
        help_text='End date for self-review period'
    )
    
    manager_review_start = models.DateField(
        help_text='Start date for manager review period'
    )
    
    manager_review_end = models.DateField(
        help_text='End date for manager review period'
    )
    
    calibration_start = models.DateField(
        null=True,
        blank=True,
        help_text='Start date for calibration period'
    )
    
    calibration_end = models.DateField(
        null=True,
        blank=True,
        help_text='End date for calibration period'
    )
    
    # Cycle configuration
    requires_goals = models.BooleanField(
        default=True,
        help_text='Whether this cycle requires goal setting'
    )
    
    requires_self_review = models.BooleanField(
        default=True,
        help_text='Whether this cycle requires self-review'
    )
    
    requires_manager_review = models.BooleanField(
        default=True,
        help_text='Whether this cycle requires manager review'
    )
    
    requires_peer_feedback = models.BooleanField(
        default=False,
        help_text='Whether this cycle requires peer feedback'
    )
    
    max_peer_feedback = models.PositiveIntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text='Maximum number of peer feedback requests per employee'
    )
    
    # Cycle settings
    goal_weight_percentage = models.PositiveIntegerField(
        default=70,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Percentage weight of goals in overall evaluation'
    )
    
    competency_weight_percentage = models.PositiveIntegerField(
        default=30,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Percentage weight of competencies in overall evaluation'
    )
    
    # Cycle metadata
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='created_cycles',
        help_text='User who created this cycle'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Whether the cycle is active'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Meta options for ReviewCycle model."""
        verbose_name = 'Review Cycle'
        verbose_name_plural = 'Review Cycles'
        ordering = ['-start_date']
    
    def __str__(self):
        """String representation of the review cycle."""
        return f"{self.name} ({self.get_cycle_type_display()})"
    
    def clean(self):
        """Validate the review cycle data."""
        super().clean()
        
        # Validate date order
        if self.start_date >= self.end_date:
            raise ValidationError('Start date must be before end date.')
        
        if self.goal_setting_start >= self.goal_setting_end:
            raise ValidationError('Goal setting start date must be before end date.')
        
        if self.self_review_start >= self.self_review_end:
            raise ValidationError('Self-review start date must be before end date.')
        
        if self.manager_review_start >= self.manager_review_end:
            raise ValidationError('Manager review start date must be before end date.')
        
        # Validate date sequence
        if self.goal_setting_end > self.self_review_start:
            raise ValidationError('Goal setting period must end before self-review starts.')
        
        if self.self_review_end > self.manager_review_start:
            raise ValidationError('Self-review period must end before manager review starts.')
        
        if self.manager_review_end > self.end_date:
            raise ValidationError('Manager review period must end before cycle ends.')
        
        # Validate calibration dates if provided
        if self.calibration_start and self.calibration_end:
            if self.calibration_start >= self.calibration_end:
                raise ValidationError('Calibration start date must be before end date.')
            if self.calibration_end > self.end_date:
                raise ValidationError('Calibration period must end before cycle ends.')
        
        # Validate weight percentages
        total_weight = self.goal_weight_percentage + self.competency_weight_percentage
        if total_weight != 100:
            raise ValidationError('Goal and competency weights must sum to 100%.')
    
    @property
    def duration_days(self):
        """Get the duration of the cycle in days."""
        return (self.end_date - self.start_date).days
    
    @property
    def is_current(self):
        """Check if the cycle is currently active."""
        today = date.today()
        return self.start_date <= today <= self.end_date and self.status == 'active'
    
    @property
    def is_goal_setting_period(self):
        """Check if we're in the goal setting period."""
        today = date.today()
        return (self.goal_setting_start <= today <= self.goal_setting_end and 
                self.status == 'active')
    
    @property
    def is_self_review_period(self):
        """Check if we're in the self-review period."""
        today = date.today()
        return (self.self_review_start <= today <= self.self_review_end and 
                self.status == 'active')
    
    @property
    def is_manager_review_period(self):
        """Check if we're in the manager review period."""
        today = date.today()
        return (self.manager_review_start <= today <= self.manager_review_end and 
                self.status == 'active')
    
    @property
    def is_calibration_period(self):
        """Check if we're in the calibration period."""
        today = date.today()
        if self.calibration_start and self.calibration_end:
            return (self.calibration_start <= today <= self.calibration_end and 
                    self.status == 'active')
        return False
    
    def get_participants(self):
        """Get all participants in this cycle."""
        return self.participants.filter(is_active=True)
    
    def get_participant_count(self):
        """Get the number of participants in this cycle."""
        return self.get_participants().count()
    
    def get_completion_percentage(self):
        """Get the completion percentage of the cycle."""
        participants = self.get_participants()
        if not participants.exists():
            return 0
        
        completed = participants.filter(
            self_review_completed=True,
            manager_review_completed=True
        ).count()
        
        return (completed / participants.count()) * 100


class CycleParticipant(models.Model):
    """
    Cycle participant model.
    
    Represents an employee's participation in a specific
    review cycle with their progress and completion status.
    """
    
    cycle = models.ForeignKey(
        ReviewCycle,
        on_delete=models.CASCADE,
        related_name='participants',
        help_text='Review cycle'
    )
    
    employee = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='cycle_participations',
        help_text='Employee participating in the cycle'
    )
    
    manager = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_cycles',
        help_text='Manager for this employee in this cycle'
    )
    
    # Participation status
    is_active = models.BooleanField(
        default=True,
        help_text='Whether the employee is actively participating'
    )
    
    # Goal setting status
    goals_set = models.BooleanField(
        default=False,
        help_text='Whether the employee has set their goals'
    )
    
    goals_approved = models.BooleanField(
        default=False,
        help_text='Whether the employee\'s goals have been approved'
    )
    
    # Review status
    self_review_completed = models.BooleanField(
        default=False,
        help_text='Whether the self-review is completed'
    )
    
    manager_review_completed = models.BooleanField(
        default=False,
        help_text='Whether the manager review is completed'
    )
    
    # Feedback status
    peer_feedback_requested = models.BooleanField(
        default=False,
        help_text='Whether peer feedback has been requested'
    )
    
    peer_feedback_completed = models.BooleanField(
        default=False,
        help_text='Whether peer feedback is completed'
    )
    
    # Completion tracking
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the cycle was completed for this employee'
    )
    
    # Notes and comments
    notes = models.TextField(
        blank=True,
        help_text='Notes about this participant\'s cycle'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Meta options for CycleParticipant model."""
        verbose_name = 'Cycle Participant'
        verbose_name_plural = 'Cycle Participants'
        unique_together = ['cycle', 'employee']
        ordering = ['employee__employee_id']
    
    def __str__(self):
        """String representation of the cycle participant."""
        return f"{self.employee.employee_id} in {self.cycle.name}"
    
    @property
    def is_fully_completed(self):
        """Check if the participant has completed all required steps."""
        completed = True
        
        if self.cycle.requires_goals:
            completed = completed and self.goals_approved
        
        if self.cycle.requires_self_review:
            completed = completed and self.self_review_completed
        
        if self.cycle.requires_manager_review:
            completed = completed and self.manager_review_completed
        
        if self.cycle.requires_peer_feedback:
            completed = completed and self.peer_feedback_completed
        
        return completed
    
    @property
    def completion_percentage(self):
        """Get the completion percentage for this participant."""
        total_steps = 0
        completed_steps = 0
        
        if self.cycle.requires_goals:
            total_steps += 1
            if self.goals_approved:
                completed_steps += 1
        
        if self.cycle.requires_self_review:
            total_steps += 1
            if self.self_review_completed:
                completed_steps += 1
        
        if self.cycle.requires_manager_review:
            total_steps += 1
            if self.manager_review_completed:
                completed_steps += 1
        
        if self.cycle.requires_peer_feedback:
            total_steps += 1
            if self.peer_feedback_completed:
                completed_steps += 1
        
        if total_steps == 0:
            return 100
        
        return (completed_steps / total_steps) * 100


class CycleTemplate(models.Model):
    """
    Cycle template model.
    
    Represents a template for creating review cycles
    with predefined settings and configurations.
    """
    
    name = models.CharField(
        max_length=200,
        help_text='Template name'
    )
    
    description = models.TextField(
        blank=True,
        help_text='Template description'
    )
    
    cycle_type = models.CharField(
        max_length=20,
        choices=ReviewCycle.TYPE_CHOICES,
        help_text='Type of review cycle'
    )
    
    # Default settings
    default_duration_days = models.PositiveIntegerField(
        default=365,
        help_text='Default duration in days'
    )
    
    goal_setting_days = models.PositiveIntegerField(
        default=30,
        help_text='Goal setting period in days'
    )
    
    self_review_days = models.PositiveIntegerField(
        default=14,
        help_text='Self-review period in days'
    )
    
    manager_review_days = models.PositiveIntegerField(
        default=14,
        help_text='Manager review period in days'
    )
    
    calibration_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Calibration period in days'
    )
    
    # Default configuration
    requires_goals = models.BooleanField(default=True)
    requires_self_review = models.BooleanField(default=True)
    requires_manager_review = models.BooleanField(default=True)
    requires_peer_feedback = models.BooleanField(default=False)
    max_peer_feedback = models.PositiveIntegerField(default=3)
    
    goal_weight_percentage = models.PositiveIntegerField(default=70)
    competency_weight_percentage = models.PositiveIntegerField(default=30)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Meta options for CycleTemplate model."""
        verbose_name = 'Cycle Template'
        verbose_name_plural = 'Cycle Templates'
        ordering = ['name']
    
    def __str__(self):
        """String representation of the cycle template."""
        return self.name
    
    def create_cycle(self, name, start_date, created_by):
        """Create a new cycle from this template."""
        end_date = start_date + timedelta(days=self.default_duration_days)
        
        cycle = ReviewCycle.objects.create(
            name=name,
            cycle_type=self.cycle_type,
            start_date=start_date,
            end_date=end_date,
            goal_setting_start=start_date,
            goal_setting_end=start_date + timedelta(days=self.goal_setting_days),
            self_review_start=start_date + timedelta(days=self.goal_setting_days + 1),
            self_review_end=start_date + timedelta(days=self.goal_setting_days + self.self_review_days + 1),
            manager_review_start=start_date + timedelta(days=self.goal_setting_days + self.self_review_days + 2),
            manager_review_end=start_date + timedelta(days=self.goal_setting_days + self.self_review_days + self.manager_review_days + 2),
            calibration_start=start_date + timedelta(days=self.goal_setting_days + self.self_review_days + self.manager_review_days + 3) if self.calibration_days else None,
            calibration_end=start_date + timedelta(days=self.goal_setting_days + self.self_review_days + self.manager_review_days + self.calibration_days + 3) if self.calibration_days else None,
            requires_goals=self.requires_goals,
            requires_self_review=self.requires_self_review,
            requires_manager_review=self.requires_manager_review,
            requires_peer_feedback=self.requires_peer_feedback,
            max_peer_feedback=self.max_peer_feedback,
            goal_weight_percentage=self.goal_weight_percentage,
            competency_weight_percentage=self.competency_weight_percentage,
            created_by=created_by
        )
        
        return cycle