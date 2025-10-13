"""
Serializers for the goals app.

This module contains serializers for goals, goal updates, and goal categories.
"""

from rest_framework import serializers
from .models import (
    Goal, GoalCategory, GoalUpdate, GoalTemplate,
    GoalVersion, BusinessObjective, GoalAlignment
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
    Serializer for Goal model.
    
    Provides full goal information including SMART criteria
    and progress tracking.
    """
    
    employee = UserListSerializer(read_only=True)
    employee_id = serializers.IntegerField(write_only=True, required=False)
    cycle_id = serializers.IntegerField(write_only=True, required=False)
    updates = GoalUpdateSerializer(many=True, read_only=True)
    
    class Meta:
        model = Goal
        fields = [
            'id', 'title', 'description', 'employee', 'employee_id',
            'cycle', 'cycle_id', 'specific', 'measurable', 'achievable',
            'relevant', 'time_bound', 'goal_type', 'priority', 'status',
            'metric', 'target_value', 'current_value', 'unit', 
            'start_date', 'target_date', 'completed_date', 'weight', 
            'approved_by', 'approved_at', 'progress_percentage', 
            'last_updated', 'notes', 'updates',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'progress_percentage', 
            'completed_date', 'approved_at', 'last_updated'
        ]
        extra_kwargs = {
            'cycle': {'required': False},
            'employee': {'required': False}
        }
    
    def create(self, validated_data):
        """
        Create a new goal.
        
        Automatically sets the employee to the current user if not provided.
        """
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