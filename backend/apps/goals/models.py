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
        ('submitted', 'Submitted'),  # Pending manager approval
        ('approved', 'Approved'),      # BR-017: Manager approval required
        ('rejected', 'Rejected'),      # Manager rejected, needs revision
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
        """Validate the goal data with SMART criteria and business rules."""
        super().clean()
        
        # BR-015: SMART validation - Validate title length (5-100 characters)
        if len(self.title) < 5 or len(self.title) > 100:
            raise ValidationError({
                'title': 'Goal title must be between 5 and 100 characters.'
            })
        
        # BR-015: SMART validation - Validate description length (20-500 characters)
        if len(self.description) < 20 or len(self.description) > 500:
            raise ValidationError({
                'description': 'Goal description must be between 20 and 500 characters. '
                              'Provide clear, specific details about what will be accomplished.'
            })
        
        # BR-015: SMART validation - Measurable metric required
        if not self.metric or len(self.metric.strip()) == 0:
            raise ValidationError({
                'metric': 'A measurable metric is required. '
                         'Examples: "Increase by 25%", "Complete 10 projects", "Reduce time to 2 hours"'
            })
        
        # BR-015: Validate metric contains measurable criteria
        metric_lower = self.metric.lower()
        measurable_indicators = [
            'increase', 'decrease', 'reduce', 'improve', 'achieve', 'complete',
            'reach', 'exceed', '%', 'percent', 'number', 'count', 'time', 'hours',
            'days', 'weeks', 'projects', 'items', 'customers', 'revenue', 'cost'
        ]
        
        # Check if metric contains numbers or measurable keywords
        has_number = any(char.isdigit() for char in self.metric)
        has_indicator = any(indicator in metric_lower for indicator in measurable_indicators)
        
        if not (has_number or has_indicator):
            raise ValidationError({
                'metric': 'Metric must contain quantifiable criteria. '
                         'Include specific numbers or measurable terms (e.g., "25%", "10 projects", "2 hours")'
            })
        
        # BR-015: SMART validation - Specific criteria
        vague_terms = ['improve', 'better', 'more', 'less', 'good', 'bad']
        if any(term in self.title.lower() and term == self.title.lower().strip() for term in vague_terms):
            raise ValidationError({
                'title': 'Goal title is too vague. Be specific about what exactly will be accomplished. '
                        'Avoid standalone vague terms like "improve" or "better".'
            })
        
        # Validate date order
        if self.start_date >= self.target_date:
            raise ValidationError({
                'target_date': 'Target date must be after start date.'
            })
        
        # BR-016: Target dates must be within the active review cycle period
        if self.cycle:
            if self.target_date < self.cycle.start_date:
                raise ValidationError({
                    'target_date': f'Target date cannot be before cycle start date ({self.cycle.start_date}).'
                })
            if self.target_date > self.cycle.end_date:
                raise ValidationError({
                    'target_date': f'Target date cannot be after cycle end date ({self.cycle.end_date}). '
                                  'Goals must be achievable within the review cycle period.'
                })
            if self.start_date < self.cycle.start_date:
                raise ValidationError({
                    'start_date': f'Start date cannot be before cycle start date ({self.cycle.start_date}).'
                })
        
        # Validate past dates
        from django.utils import timezone
        today = timezone.now().date()
        if self.target_date < today and not self.pk:
            raise ValidationError({
                'target_date': 'Target date cannot be in the past. Goals must have future completion dates.'
            })
        
        # Validate progress percentage
        if self.progress_percentage < 0 or self.progress_percentage > 100:
            raise ValidationError('Progress percentage must be between 0 and 100.')
        
        # Validate weight
        if self.weight < 1 or self.weight > 100:
            raise ValidationError({
                'weight': 'Weight must be between 1 and 100%.'
            })
        
        # BR-012: Validate maximum 5 goals per employee per cycle
        if not self.pk:  # Only for new goals
            employee_goals_count = Goal.objects.filter(
                employee=self.employee,
                cycle=self.cycle
            ).exclude(status='cancelled').count()
            
            if employee_goals_count >= 5:
                raise ValidationError({
                    'non_field_errors': f'Maximum of 5 goals allowed per employee per cycle. '
                                       f'You currently have {employee_goals_count} goals. '
                                       f'Please complete or cancel existing goals before adding new ones.'
                })
        
        # BR-013: Validate total weight equals 100% when submitting
        if self.employee and self.cycle:
            # Only enforce 100% total when status is submitted, approved, or in_progress
            if self.status in ['submitted', 'approved', 'in_progress']:
                # Get all goals for this employee in this cycle (excluding cancelled)
                existing_goals = Goal.objects.filter(
                    employee=self.employee,
                    cycle=self.cycle
                ).exclude(status='cancelled')
                
                if self.pk:
                    existing_goals = existing_goals.exclude(pk=self.pk)
                
                total_weight = sum(g.weight for g in existing_goals) + self.weight
                
                if total_weight != 100:
                    raise ValidationError({
                        'weight': f'Total weight must equal exactly 100% when submitting goals. '
                                 f'Current total: {total_weight}%. '
                                 f'Please adjust goal weights so they sum to 100%.'
                    })
            else:
                # For draft status, just ensure we don't exceed 100%
                existing_goals = Goal.objects.filter(
                    employee=self.employee,
                    cycle=self.cycle
                ).exclude(status='cancelled')
                
                if self.pk:
                    existing_goals = existing_goals.exclude(pk=self.pk)
                
                total_weight = sum(g.weight for g in existing_goals) + self.weight
                
                if total_weight > 100:
                    raise ValidationError({
                        'weight': f'Total weight cannot exceed 100%. Current total: {total_weight}%. '
                                 f'You can have less than 100% for draft goals.'
                    })
    
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
        """
        Approve the goal and create version history (BR-017).
        Manager approval required before goals become active.
        """
        self.status = 'approved'
        self.approved_by = approved_by
        from django.utils import timezone
        self.approved_at = timezone.now()
        self.save()
        
        # Create version history
        self.create_version('approved', approved_by, 'Goal approved by manager')
    
    def reject(self, rejected_by, feedback_comment):
        """
        Reject the goal and create version history (BR-018).
        Manager feedback is mandatory for goal rejections.
        """
        if not feedback_comment or len(feedback_comment.strip()) < 10:
            raise ValidationError(
                'Detailed feedback is required when rejecting goals. '
                'Provide at least 10 characters of specific guidance.'
            )
        
        self.status = 'rejected'
        self.approved_by = None  # Clear previous approval
        self.approved_at = None
        self.save()
        
        # Create version history
        self.create_version('rejected', rejected_by, f'Goal rejected: {feedback_comment[:100]}')
    
    def can_be_edited_by(self, user):
        """
        Check if goal can be edited by user (BR-021).
        Goal editing allowed until manager approval.
        """
        # Employees can edit their own draft or rejected goals
        if user == self.employee:
            return self.status in ['draft', 'rejected']
        
        # Managers cannot directly edit goals (only provide feedback)
        return False
    
    def create_version(self, change_type, changed_by, change_summary=''):
        """Create a version history entry for this goal."""
        # Get the next version number
        last_version = self.versions.order_by('-version_number').first()
        next_version = (last_version.version_number + 1) if last_version else 1
        
        # Create snapshot of current goal data
        data_snapshot = {
            'title': self.title,
            'description': self.description,
            'metric': self.metric,
            'target_value': str(self.target_value) if self.target_value else None,
            'current_value': str(self.current_value) if self.current_value else None,
            'unit': self.unit,
            'start_date': str(self.start_date),
            'target_date': str(self.target_date),
            'weight': self.weight,
            'status': self.status,
            'priority': self.priority,
            'goal_type': self.goal_type,
            'progress_percentage': self.progress_percentage,
        }
        
        GoalVersion.objects.create(
            goal=self,
            version_number=next_version,
            changed_by=changed_by,
            change_type=change_type,
            data_snapshot=data_snapshot,
            change_summary=change_summary
        )
    
    def delete(self, *args, **kwargs):
        """
        Override delete to prevent deletion of approved goals (BR-014).
        Goals cannot be deleted once approved, only cancelled.
        """
        if self.status in ['approved', 'in_progress', 'completed']:
            raise ValidationError({
                'non_field_errors': 'Cannot delete approved goals. '
                                   'Goals that have been approved can only be cancelled or edited. '
                                   'This maintains version history and audit trail.'
            })
        super().delete(*args, **kwargs)
    
    def save(self, *args, **kwargs):
        """Override save to create version history automatically."""
        is_new = not self.pk
        old_status = None
        
        if not is_new:
            try:
                old_goal = Goal.objects.get(pk=self.pk)
                old_status = old_goal.status
            except Goal.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # Create version history for status changes
        if is_new:
            self.create_version('created', self.employee, 'Goal created')
        elif old_status and old_status != self.status:
            change_map = {
                'submitted': ('submitted', 'Goal submitted for approval'),
                'approved': ('approved', 'Goal approved'),
                'in_progress': ('updated', 'Goal marked as in progress'),
                'completed': ('completed', 'Goal completed'),
                'cancelled': ('cancelled', 'Goal cancelled'),
            }
            if self.status in change_map:
                change_type, summary = change_map[self.status]
                self.create_version(change_type, self.employee, summary)


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


class GoalFeedback(models.Model):
    """
    Manager feedback on employee goals.
    BR-018: Manager feedback is mandatory for goal rejections.
    Tracks all review feedback and decisions.
    """
    
    FEEDBACK_TYPE_CHOICES = [
        ('approval', 'Approval'),
        ('request_changes', 'Request Changes'),
        ('rejection', 'Rejection'),
        ('suggestion', 'Suggestion'),
        ('alignment_comment', 'Alignment Comment'),
    ]
    
    goal = models.ForeignKey(
        Goal,
        on_delete=models.CASCADE,
        related_name='feedback',
        help_text='Goal being reviewed'
    )
    
    manager = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='goal_feedback_given',
        help_text='Manager providing feedback'
    )
    
    feedback_type = models.CharField(
        max_length=20,
        choices=FEEDBACK_TYPE_CHOICES,
        help_text='Type of feedback being provided'
    )
    
    comments = models.TextField(
        help_text='Manager feedback comments'
    )
    
    # SMART Criteria Review Checklist
    smart_specific = models.BooleanField(
        default=True,
        help_text='Goal clearly defines what will be accomplished'
    )
    
    smart_measurable = models.BooleanField(
        default=True,
        help_text='Quantifiable success metrics are present'
    )
    
    smart_achievable = models.BooleanField(
        default=True,
        help_text='Goal is realistic given resources and timeframe'
    )
    
    smart_relevant = models.BooleanField(
        default=True,
        help_text='Aligns with business objectives and role responsibilities'
    )
    
    smart_time_bound = models.BooleanField(
        default=True,
        help_text='Clear deadline within review cycle'
    )
    
    # Additional Review Fields
    alignment_score = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Business alignment rating (1-5)'
    )
    
    challenge_level = models.CharField(
        max_length=20,
        choices=[
            ('too_easy', 'Too Easy'),
            ('appropriate', 'Appropriate'),
            ('too_ambitious', 'Too Ambitious'),
        ],
        null=True,
        blank=True,
        help_text='Manager assessment of goal difficulty'
    )
    
    suggested_modifications = models.TextField(
        blank=True,
        help_text='Specific suggestions for goal improvement'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Meta options for GoalFeedback model."""
        verbose_name = 'Goal Feedback'
        verbose_name_plural = 'Goal Feedback'
        ordering = ['-created_at']
    
    def __str__(self):
        """String representation of the goal feedback."""
        return f"{self.feedback_type} for {self.goal.title} by {self.manager.full_name}"
    
    def clean(self):
        """
        Validate feedback data.
        BR-018: Manager feedback is mandatory for goal rejections.
        BR-020: Managers can only approve goals for direct reports.
        """
        super().clean()
        
        # BR-018: Ensure comments provided for rejections and change requests
        if self.feedback_type in ['rejection', 'request_changes']:
            if not self.comments or len(self.comments.strip()) < 10:
                raise ValidationError({
                    'comments': 'Detailed feedback is required when requesting changes or rejecting goals. '
                               'Provide at least 10 characters of specific guidance.'
                })
        
        # BR-020: Verify manager-employee relationship
        if self.goal and self.manager:
            # Check if manager is the employee's direct manager
            if hasattr(self.goal.employee, 'manager') and self.goal.employee.manager != self.manager:
                # Allow if user is HR
                if self.manager.role not in ['hr', 'admin']:
                    raise ValidationError({
                        'manager': 'You can only review goals for your direct reports. '
                                  'This goal belongs to an employee who does not report to you.'
                    })
    
    @property
    def smart_compliance_score(self):
        """Calculate SMART compliance percentage."""
        criteria = [
            self.smart_specific,
            self.smart_measurable,
            self.smart_achievable,
            self.smart_relevant,
            self.smart_time_bound
        ]
        return (sum(criteria) / len(criteria)) * 100