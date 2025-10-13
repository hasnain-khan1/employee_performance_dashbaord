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
            'id', 'goal', 'progress_percentage', 'status_update',
            'achievements', 'challenges', 'next_steps',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


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
            'metric', 'target_value', 'current_value', 'start_date',
            'target_date', 'completion_date', 'weight', 'progress_percentage',
            'category', 'manager', 'is_stretch_goal', 'updates',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'progress_percentage'
        ]
    
    def create(self, validated_data):
        """
        Create a new goal.
        
        Automatically sets the employee to the current user if not provided.
        """
        request = self.context.get('request')
        
        # Set employee to current user if not provided
        if not validated_data.get('employee_id') and request and request.user:
            validated_data['employee_id'] = request.user.id
        
        # Set manager to current user's manager if not provided
        if not validated_data.get('manager') and request and request.user:
            validated_data['manager'] = request.user.manager
        
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
            'id', 'name', 'description', 'color', 'icon',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']