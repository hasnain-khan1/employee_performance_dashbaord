"""
Goals models for the EPMS system.

This module contains models for SMART goals management,
including goal creation, tracking, and evaluation.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


class Goal(models.Model):
    """
    Goal model for performance management.
    
    Represents a SMART goal with specific, measurable,
    achievable, relevant, and time-bound criteria.
    """
    
    # Goal status choices
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('overdue', 'Overdue'),
    ]
    
    # Goal priority choices
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    # Goal type choices
    TYPE_CHOICES = [
        ('performance', 'Performance'),
        ('development', 'Development'),
        ('behavioral', 'Behavioral'),
        ('project', 'Project'),
        ('stretch', 'Stretch'),
    ]
    
    # Basic information
    title = models.CharField(
        max_length=200,
        help_text='Goal title'
    )
    
    description = models.TextField(
        help_text='Detailed goal description'
    )
    
    employee = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='goals',
        help_text='Employee who owns this goal'
    )
    
    cycle = models.ForeignKey(
        'cycles.ReviewCycle',
        on_delete=models.CASCADE,
        related_name='goals',
        help_text='Review cycle this goal belongs to'
    )
    
    # SMART criteria
    specific = models.TextField(
        help_text='Specific: What exactly will be accomplished?'
    )
    
    measurable = models.TextField(
        help_text='Measurable: How will success be measured?'
    )
    
    achievable = models.TextField(
        help_text='Achievable: Is this goal realistic and attainable?'
    )
    
    relevant = models.TextField(
        help_text='Relevant: How does this align with broader objectives?'
    )
    
    time_bound = models.TextField(
        help_text='Time-bound: What is the deadline and timeline?'
    )
    
    # Goal details
    goal_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='performance',
        help_text='Type of goal'
    )
    
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        help_text='Goal priority level'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text='Current status of the goal'
    )
    
    # Metrics and measurement
    metric = models.CharField(
        max_length=100,
        help_text='Primary metric for measuring success'
    )
    
    target_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Target value for the metric'
    )
    
    current_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Current value of the metric'
    )
    
    unit = models.CharField(
        max_length=50,
        blank=True,
        help_text='Unit of measurement (e.g., %, $, hours)'
    )
    
    # Timeline
    start_date = models.DateField(
        help_text='Goal start date'
    )
    
    target_date = models.DateField(
        help_text='Goal target completion date'
    )
    
    completed_date = models.DateField(
        null=True,
        blank=True,
        help_text='Actual completion date'
    )
    
    # Weight and scoring
    weight = models.PositiveIntegerField(
        default=10,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text='Weight of this goal in overall evaluation (1-100)'
    )
    
    # Approval and review
    approved_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_goals',
        help_text='Manager who approved this goal'
    )
    
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the goal was approved'
    )
    
    # Progress tracking
    progress_percentage = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Current progress percentage (0-100)'
    )
    
    last_updated = models.DateTimeField(
        auto_now=True,
        help_text='Last time the goal was updated'
    )
    
    # Notes and comments
    notes = models.TextField(
        blank=True,
        help_text='Additional notes about the goal'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Meta options for Goal model."""
        verbose_name = 'Goal'
        verbose_name_plural = 'Goals'
        ordering = ['-created_at']
    
    def __str__(self):
        """String representation of the goal."""
        return f"{self.title} - {self.employee.employee_id}"
    
    def clean(self):
        """Validate the goal data."""
        super().clean()
        
        # Validate date order
        if self.start_date >= self.target_date:
            raise ValidationError('Start date must be before target date.')
        
        # Validate progress percentage
        if self.progress_percentage < 0 or self.progress_percentage > 100:
            raise ValidationError('Progress percentage must be between 0 and 100.')
        
        # Validate weight
        if self.weight < 1 or self.weight > 100:
            raise ValidationError('Weight must be between 1 and 100.')
    
    @property
    def is_overdue(self):
        """Check if the goal is overdue."""
        from django.utils import timezone
        return (self.status in ['in_progress', 'approved'] and 
                self.target_date < timezone.now().date() and 
                not self.completed_date)
    
    @property
    def days_remaining(self):
        """Get the number of days remaining to complete the goal."""
        from django.utils import timezone
        today = timezone.now().date()
        if self.completed_date:
            return 0
        return max(0, (self.target_date - today).days)
    
    @property
    def completion_rate(self):
        """Get the completion rate based on progress and time."""
        if self.completed_date:
            return 100
        
        from django.utils import timezone
        today = timezone.now().date()
        total_days = (self.target_date - self.start_date).days
        elapsed_days = (today - self.start_date).days
        
        if total_days <= 0:
            return 0
        
        time_completion = min(100, (elapsed_days / total_days) * 100)
        return (self.progress_percentage + time_completion) / 2
    
    def update_progress(self, progress_percentage, current_value=None, notes=None):
        """Update the goal progress."""
        self.progress_percentage = progress_percentage
        
        if current_value is not None:
            self.current_value = current_value
        
        if notes:
            self.notes = f"{self.notes}\n{notes}" if self.notes else notes
        
        # Check if goal is completed
        if progress_percentage >= 100:
            self.status = 'completed'
            if not self.completed_date:
                from django.utils import timezone
                self.completed_date = timezone.now().date()
        
        # Check if goal is overdue
        elif self.is_overdue:
            self.status = 'overdue'
        
        self.save()
    
    def approve(self, approved_by):
        """Approve the goal."""
        self.status = 'approved'
        self.approved_by = approved_by
        from django.utils import timezone
        self.approved_at = timezone.now()
        self.save()


class GoalUpdate(models.Model):
    """
    Goal update model for tracking progress.
    
    Represents updates made to goals with progress
    information and comments.
    """
    
    goal = models.ForeignKey(
        Goal,
        on_delete=models.CASCADE,
        related_name='updates',
        help_text='Goal being updated'
    )
    
    updated_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='goal_updates',
        help_text='User who made the update'
    )
    
    progress_percentage = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Progress percentage at the time of update'
    )
    
    current_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Current value of the metric'
    )
    
    comments = models.TextField(
        help_text='Comments about the progress update'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        """Meta options for GoalUpdate model."""
        verbose_name = 'Goal Update'
        verbose_name_plural = 'Goal Updates'
        ordering = ['-created_at']
    
    def __str__(self):
        """String representation of the goal update."""
        return f"Update for {self.goal.title} - {self.progress_percentage}%"


class GoalCategory(models.Model):
    """
    Goal category model for organizing goals.
    
    Represents categories that goals can be assigned to
    for better organization and reporting.
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text='Category name'
    )
    
    description = models.TextField(
        blank=True,
        help_text='Category description'
    )
    
    color = models.CharField(
        max_length=7,
        default='#007bff',
        help_text='Color code for the category (hex)'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Whether the category is active'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Meta options for GoalCategory model."""
        verbose_name = 'Goal Category'
        verbose_name_plural = 'Goal Categories'
        ordering = ['name']
    
    def __str__(self):
        """String representation of the goal category."""
        return self.name