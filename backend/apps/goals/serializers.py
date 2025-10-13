"""
Serializers for the goals app.

This module contains serializers for goals, goal updates, and goal categories.
Implements BR-012, BR-013, BR-014, BR-015, BR-016 business rules.
"""

from django.db import models
from rest_framework import serializers
from .models import (
    Goal, GoalCategory, GoalUpdate, GoalTemplate,
    GoalVersion, BusinessObjective, GoalAlignment, GoalFeedback
)
from apps.accounts.serializers import UserListSerializer


class GoalUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for GoalUpdate model.
    
    Handles goal progress updates and status changes.
    """
    
    class Meta:
        model = GoalUpdate
        fields = [
            'id', 'goal', 'updated_by', 'progress_percentage',
            'current_value', 'comments', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_by']


class GoalSerializer(serializers.ModelSerializer):
    """
    Enhanced serializer for Goal model with SMART validation.
    Implements BR-012, BR-013, BR-014, BR-015, BR-016.
    """
    
    employee = UserListSerializer(read_only=True)
    employee_id = serializers.IntegerField(write_only=True, required=False)
    cycle_id = serializers.IntegerField(write_only=True, required=False)
    updates = GoalUpdateSerializer(many=True, read_only=True)
    feedback = serializers.SerializerMethodField()  # Latest feedback
    
    # Read-only fields for display
    is_overdue = serializers.BooleanField(read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    completion_rate = serializers.FloatField(read_only=True)
    current_weight_total = serializers.SerializerMethodField()
    remaining_weight = serializers.SerializerMethodField()
    goals_count = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    
    class Meta:
        model = Goal
        fields = [
            'id', 'title', 'description', 'employee', 'employee_id',
            'cycle', 'cycle_id', 'specific', 'measurable', 'achievable',
            'relevant', 'time_bound', 'goal_type', 'priority', 'status',
            'metric', 'target_value', 'current_value', 'unit', 
            'start_date', 'target_date', 'completed_date', 'weight', 
            'approved_by', 'approved_at', 'progress_percentage', 
            'last_updated', 'notes', 'updates', 'feedback',
            'is_overdue', 'days_remaining', 'completion_rate',
            'current_weight_total', 'remaining_weight', 'goals_count', 'can_edit',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'progress_percentage', 
            'completed_date', 'approved_at', 'last_updated'
        ]
        extra_kwargs = {
            'cycle': {'required': False},
            'employee': {'required': False},
            'title': {
                'min_length': 5,
                'max_length': 100,
                'help_text': 'Goal title (5-100 characters). Be specific and avoid vague terms.'
            },
            'description': {
                'min_length': 20,
                'max_length': 500,
                'help_text': 'Detailed description (20-500 characters). Clearly define what will be accomplished.'
            },
            'metric': {
                'required': True,
                'help_text': 'Measurable criteria. Include specific numbers or measurable terms (e.g., "25%", "10 projects")'
            },
            'target_date': {
                'help_text': 'Target completion date. Must be within review cycle period.'
            },
            'weight': {
                'help_text': 'Goal weight (1-100%). Total across all goals must equal 100% when submitting.'
            }
        }
    
    def get_current_weight_total(self, obj):
        """Calculate current weight total for this employee's goals."""
        if not obj.employee or not obj.cycle:
            return 0
        total = Goal.objects.filter(
            employee=obj.employee,
            cycle=obj.cycle
        ).exclude(status='cancelled').exclude(pk=obj.pk).aggregate(
            total=models.Sum('weight')
        )['total'] or 0
        return total + obj.weight
    
    def get_remaining_weight(self, obj):
        """Calculate remaining weight available."""
        current_total = self.get_current_weight_total(obj)
        return 100 - current_total
    
    def get_goals_count(self, obj):
        """Get count of active goals for this employee."""
        if not obj.employee or not obj.cycle:
            return 0
        return Goal.objects.filter(
            employee=obj.employee,
            cycle=obj.cycle
        ).exclude(status='cancelled').count()
    
    def get_feedback(self, obj):
        """Get latest feedback for this goal."""
        latest_feedback = obj.feedback.order_by('-created_at').first()
        if latest_feedback:
            return GoalFeedbackSerializer(latest_feedback).data
        return None
    
    def get_can_edit(self, obj):
        """Check if current user can edit this goal (BR-021)."""
        request = self.context.get('request')
        if request and request.user:
            return obj.can_be_edited_by(request.user)
        return False
    
    def validate(self, data):
        """
        Enhanced validation implementing all business rules.
        BR-012 through BR-016.
        """
        # Get employee and cycle from context if not in data
        request = self.context.get('request')
        employee = data.get('employee') or (self.instance.employee if self.instance else None) or (request.user if request else None)
        cycle = data.get('cycle') or (self.instance.cycle if self.instance else None)
        
        # BR-012: Maximum 5 goals per employee per cycle
        if not self.instance:  # Only for new goals
            if employee and cycle:
                existing_count = Goal.objects.filter(
                    employee=employee,
                    cycle=cycle
                ).exclude(status='cancelled').count()
                
                if existing_count >= 5:
                    raise serializers.ValidationError({
                        'non_field_errors': f'Maximum of 5 goals allowed per employee per cycle. '
                                           f'You currently have {existing_count} goals. '
                                           f'Complete or cancel existing goals before creating new ones.'
                    })
        
        # BR-013: Validate weight totals
        # Check if we're updating status to submitted/approved or if weight is changing
        status = data.get('status', self.instance.status if self.instance else 'draft')
        weight_changed = 'weight' in data
        status_changed = 'status' in data and self.instance and data['status'] != self.instance.status
        
        # Validate weight totals when:
        # 1. Weight is being changed, OR
        # 2. Status is being changed to submitted/approved/in_progress
        if (weight_changed or (status_changed and status in ['submitted', 'approved', 'in_progress'])) and employee and cycle:
            # Get existing goals weight
            existing_goals = Goal.objects.filter(
                employee=employee,
                cycle=cycle
            ).exclude(status='cancelled')
            
            if self.instance:
                existing_goals = existing_goals.exclude(pk=self.instance.pk)
            
            existing_weight = sum(g.weight for g in existing_goals)
            current_weight = data.get('weight', self.instance.weight if self.instance else 0)
            new_total = existing_weight + current_weight
            
            # Enforce 100% total for submitted/approved goals
            if status in ['submitted', 'approved', 'in_progress']:
                if new_total != 100:
                    raise serializers.ValidationError({
                        'status': f'Cannot submit goals for approval. Total weight must equal exactly 100%. '
                                 f'Current total: {new_total}%. '
                                 f'Existing goals weight: {existing_weight}%. '
                                 f'This goal weight: {current_weight}%. '
                                 f'Adjust goal weights so they sum to 100%.'
                    })
            elif weight_changed:
                # For draft, just prevent exceeding 100%
                if new_total > 100:
                    raise serializers.ValidationError({
                        'weight': f'Total weight cannot exceed 100%. '
                                 f'Current total would be: {new_total}%. '
                                 f'Existing goals weight: {existing_weight}%. '
                                 f'Maximum weight for this goal: {100 - existing_weight}%.'
                    })
        
        # BR-015: SMART validation - Measurable metric required
        if 'metric' in data:
            metric = data['metric'].strip()
            if not metric:
                raise serializers.ValidationError({
                    'metric': 'A measurable metric is required. '
                             'Examples: "Increase by 25%", "Complete 10 projects", "Reduce time to 2 hours"'
                })
            
            # Check for quantifiable criteria
            metric_lower = metric.lower()
            has_number = any(char.isdigit() for char in metric)
            measurable_keywords = [
                'increase', 'decrease', 'reduce', 'improve', 'achieve', 'complete',
                '%', 'percent', 'hours', 'days', 'projects', 'items'
            ]
            has_keyword = any(keyword in metric_lower for keyword in measurable_keywords)
            
            if not (has_number or has_keyword):
                raise serializers.ValidationError({
                    'metric': 'Metric must contain quantifiable criteria. '
                             'Include specific numbers or measurable terms.'
                })
        
        # BR-016: Target dates must be within review cycle period
        if 'target_date' in data and cycle:
            target_date = data['target_date']
            if target_date < cycle.start_date:
                raise serializers.ValidationError({
                    'target_date': f'Target date cannot be before cycle start date ({cycle.start_date}).'
                })
            if target_date > cycle.end_date:
                raise serializers.ValidationError({
                    'target_date': f'Target date cannot be after cycle end date ({cycle.end_date}). '
                                  'Goals must be achievable within the review cycle period.'
                })
        
        return data
    
    def create(self, validated_data):
        """
        Create a new goal with automatic version tracking.
        """
        from django.db import models as django_models
        
        # Remove _id fields that will be set by the view
        validated_data.pop('employee_id', None)
        validated_data.pop('cycle_id', None)
        
        return super().create(validated_data)


class GoalListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing goals.
    """
    
    employee = UserListSerializer(read_only=True)
    
    class Meta:
        model = Goal
        fields = [
            'id', 'title', 'description', 'employee', 'goal_type',
            'priority', 'status', 'progress_percentage', 'start_date',
            'target_date', 'weight', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'progress_percentage']


class GoalCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for GoalCategory model.
    
    Manages goal categories for organization.
    """
    
    class Meta:
        model = GoalCategory
        fields = [
            'id', 'name', 'description', 'color',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class GoalTemplateSerializer(serializers.ModelSerializer):
    """Serializer for GoalTemplate model."""
    
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = GoalTemplate
        fields = [
            'id', 'name', 'description', 'goal_type',
            'specific_template', 'measurable_template', 'achievable_template',
            'relevant_template', 'time_bound_template', 'guidance', 'example',
            'category', 'category_name', 'is_active', 'usage_count',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'usage_count', 'created_at', 'updated_at']


class GoalVersionSerializer(serializers.ModelSerializer):
    """Serializer for GoalVersion model."""
    
    changed_by_name = serializers.CharField(source='changed_by.full_name', read_only=True)
    
    class Meta:
        model = GoalVersion
        fields = [
            'id', 'goal', 'version_number', 'changed_by', 'changed_by_name',
            'change_type', 'data_snapshot', 'change_summary', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class BusinessObjectiveSerializer(serializers.ModelSerializer):
    """Serializer for BusinessObjective model."""
    
    owner_name = serializers.CharField(source='owner.full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    aligned_goals_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = BusinessObjective
        fields = [
            'id', 'name', 'description', 'department', 'department_name',
            'priority', 'target_date', 'owner', 'owner_name', 'status',
            'is_active', 'aligned_goals_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'aligned_goals_count', 'created_at', 'updated_at']


class GoalAlignmentSerializer(serializers.ModelSerializer):
    """Serializer for GoalAlignment model."""
    
    goal_title = serializers.CharField(source='goal.title', read_only=True)
    objective_name = serializers.CharField(source='objective.name', read_only=True)
    
    class Meta:
        model = GoalAlignment
        fields = [
            'id', 'goal', 'goal_title', 'objective', 'objective_name',
            'alignment_strength', 'justification', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class GoalFeedbackSerializer(serializers.ModelSerializer):
    """
    Serializer for GoalFeedback model.
    Implements BR-018, BR-020.
    """
    
    manager_name = serializers.CharField(source='manager.full_name', read_only=True)
    goal_title = serializers.CharField(source='goal.title', read_only=True)
    smart_compliance_score = serializers.FloatField(read_only=True)
    
    class Meta:
        model = GoalFeedback
        fields = [
            'id', 'goal', 'goal_title', 'manager', 'manager_name',
            'feedback_type', 'comments', 'smart_specific', 'smart_measurable',
            'smart_achievable', 'smart_relevant', 'smart_time_bound',
            'smart_compliance_score', 'alignment_score', 'challenge_level',
            'suggested_modifications', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'manager', 'created_at', 'updated_at']
        
    def validate(self, data):
        """
        Validate feedback data according to business rules.
        BR-018: Manager feedback is mandatory for goal rejections.
        """
        # BR-018: Ensure detailed comments for rejections and change requests
        if data.get('feedback_type') in ['rejection', 'request_changes']:
            comments = data.get('comments', '').strip()
            if not comments or len(comments) < 10:
                raise serializers.ValidationError({
                    'comments': 'Detailed feedback is required when requesting changes or rejecting goals. '
                               'Provide at least 10 characters of specific guidance for the employee.'
                })
        
        return data
    
    def create(self, validated_data):
        """Create feedback and automatically set manager from request."""
        request = self.context.get('request')
        if request and request.user:
            validated_data['manager'] = request.user
        return super().create(validated_data)