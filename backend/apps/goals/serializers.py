"""
Serializers for the goals app.

This module contains serializers for goals, goal updates, and goal categories.
"""

from rest_framework import serializers
from .models import Goal, GoalCategory, GoalUpdate
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