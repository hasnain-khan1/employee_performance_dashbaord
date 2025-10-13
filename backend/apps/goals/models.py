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
        
        # Validate maximum 5 goals per employee per cycle
        if not self.pk:  # Only for new goals
            employee_goals_count = Goal.objects.filter(
                employee=self.employee,
                cycle=self.cycle
            ).exclude(status='cancelled').count()
            
            if employee_goals_count >= 5:
                raise ValidationError(
                    'Maximum of 5 goals allowed per employee per cycle. '
                    'Please cancel or complete existing goals before adding new ones.'
                )
        
        # Validate total weight doesn't exceed 100%
        if self.employee and self.cycle:
            # Get all goals for this employee in this cycle (excluding this one if updating)
            existing_goals = Goal.objects.filter(
                employee=self.employee,
                cycle=self.cycle
            ).exclude(status='cancelled')
            
            if self.pk:
                existing_goals = existing_goals.exclude(pk=self.pk)
            
            total_weight = sum(g.weight for g in existing_goals) + self.weight
            
            if total_weight > 100:
                raise ValidationError(
                    f'Total weight cannot exceed 100%. Current total: {total_weight}%. '
                    f'Please adjust goal weights.'
                )
    
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


class GoalTemplate(models.Model):
    """
    SMART goal template for guided goal creation.
    
    Provides pre-defined SMART goal templates to help employees
    create well-structured goals.
    """
    
    name = models.CharField(
        max_length=200,
        help_text='Template name'
    )
    
    description = models.TextField(
        help_text='Template description'
    )
    
    goal_type = models.CharField(
        max_length=20,
        choices=Goal.TYPE_CHOICES,
        help_text='Type of goal this template is for'
    )
    
    # SMART criteria templates with guidance
    specific_template = models.TextField(
        help_text='Template for specific criteria with placeholders'
    )
    
    measurable_template = models.TextField(
        help_text='Template for measurable criteria with placeholders'
    )
    
    achievable_template = models.TextField(
        help_text='Template for achievable criteria with placeholders'
    )
    
    relevant_template = models.TextField(
        help_text='Template for relevant criteria with placeholders'
    )
    
    time_bound_template = models.TextField(
        help_text='Template for time-bound criteria with placeholders'
    )
    
    # Guidance and tips
    guidance = models.TextField(
        blank=True,
        help_text='Guidance for using this template'
    )
    
    example = models.TextField(
        blank=True,
        help_text='Example goal using this template'
    )
    
    category = models.ForeignKey(
        GoalCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='templates',
        help_text='Category this template belongs to'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Whether the template is active'
    )
    
    usage_count = models.PositiveIntegerField(
        default=0,
        help_text='Number of times this template has been used'
    )
    
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_goal_templates',
        help_text='User who created this template'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Meta options for GoalTemplate model."""
        verbose_name = 'Goal Template'
        verbose_name_plural = 'Goal Templates'
        ordering = ['-usage_count', 'name']
    
    def __str__(self):
        """String representation of the goal template."""
        return f"{self.name} ({self.goal_type})"


class GoalVersion(models.Model):
    """
    Goal version history for tracking changes.
    
    Maintains a history of all changes made to a goal
    for audit and tracking purposes.
    """
    
    goal = models.ForeignKey(
        Goal,
        on_delete=models.CASCADE,
        related_name='versions',
        help_text='Goal this version belongs to'
    )
    
    version_number = models.PositiveIntegerField(
        help_text='Version number'
    )
    
    changed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='goal_version_changes',
        help_text='User who made the change'
    )
    
    change_type = models.CharField(
        max_length=20,
        choices=[
            ('created', 'Created'),
            ('updated', 'Updated'),
            ('submitted', 'Submitted'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('progress_updated', 'Progress Updated'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        help_text='Type of change made'
    )
    
    # Snapshot of goal data at this version
    data_snapshot = models.JSONField(
        help_text='JSON snapshot of goal data at this version'
    )
    
    change_summary = models.TextField(
        blank=True,
        help_text='Summary of changes made'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        """Meta options for GoalVersion model."""
        verbose_name = 'Goal Version'
        verbose_name_plural = 'Goal Versions'
        ordering = ['-created_at']
        unique_together = ['goal', 'version_number']
    
    def __str__(self):
        """String representation of the goal version."""
        return f"{self.goal.title} v{self.version_number}"


class BusinessObjective(models.Model):
    """
    Business objective model for organizational alignment.
    
    Represents high-level business objectives that goals
    can be aligned to.
    """
    
    name = models.CharField(
        max_length=200,
        help_text='Objective name'
    )
    
    description = models.TextField(
        help_text='Objective description'
    )
    
    department = models.ForeignKey(
        'org.Department',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='objectives',
        help_text='Department this objective belongs to'
    )
    
    priority = models.CharField(
        max_length=10,
        choices=Goal.PRIORITY_CHOICES,
        default='medium',
        help_text='Objective priority level'
    )
    
    target_date = models.DateField(
        help_text='Target completion date'
    )
    
    owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='owned_objectives',
        help_text='Executive owner of this objective'
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('planning', 'Planning'),
            ('active', 'Active'),
            ('on_track', 'On Track'),
            ('at_risk', 'At Risk'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        default='planning',
        help_text='Current status of the objective'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Whether the objective is active'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Meta options for BusinessObjective model."""
        verbose_name = 'Business Objective'
        verbose_name_plural = 'Business Objectives'
        ordering = ['-priority', 'target_date']
    
    def __str__(self):
        """String representation of the business objective."""
        return self.name
    
    @property
    def aligned_goals_count(self):
        """Get the number of goals aligned to this objective."""
        return self.aligned_goals.count()


class GoalAlignment(models.Model):
    """
    Goal alignment model for linking goals to business objectives.
    
    Represents the alignment between individual goals and
    organizational objectives.
    """
    
    goal = models.ForeignKey(
        Goal,
        on_delete=models.CASCADE,
        related_name='alignments',
        help_text='Goal being aligned'
    )
    
    objective = models.ForeignKey(
        BusinessObjective,
        on_delete=models.CASCADE,
        related_name='aligned_goals',
        help_text='Business objective this goal aligns to'
    )
    
    alignment_strength = models.CharField(
        max_length=20,
        choices=[
            ('weak', 'Weak'),
            ('moderate', 'Moderate'),
            ('strong', 'Strong'),
            ('critical', 'Critical'),
        ],
        default='moderate',
        help_text='Strength of alignment'
    )
    
    justification = models.TextField(
        blank=True,
        help_text='Justification for how this goal aligns to the objective'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Meta options for GoalAlignment model."""
        verbose_name = 'Goal Alignment'
        verbose_name_plural = 'Goal Alignments'
        unique_together = ['goal', 'objective']
    
    def __str__(self):
        """String representation of the goal alignment."""
        return f"{self.goal.title} → {self.objective.name}"