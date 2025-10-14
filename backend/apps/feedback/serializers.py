"""
Serializers for the feedback app.

This module contains serializers for feedback requests,
responses, templates, and manager feedback.
"""

from rest_framework import serializers
from .models import FeedbackRequest, FeedbackResponse, FeedbackTemplate, ManagerFeedback
from apps.accounts.serializers import UserListSerializer


class FeedbackRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for FeedbackRequest model.
    
    Provides full feedback request information including
    requester and recipient details.
    """
    
    requester = UserListSerializer(read_only=True)
    recipient = UserListSerializer(read_only=True)
    requester_id = serializers.IntegerField(write_only=True, required=False)
    recipient_id = serializers.IntegerField(write_only=True)
    cycle_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = FeedbackRequest
        fields = [
            'id', 'requester', 'recipient', 'cycle', 'status',
            'message', 'due_date', 'submitted_at',
            'requester_id', 'recipient_id', 'cycle_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'submitted_at']


class FeedbackRequestListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing feedback requests.
    """
    
    requester = UserListSerializer(read_only=True)
    recipient = UserListSerializer(read_only=True)
    
    class Meta:
        model = FeedbackRequest
        fields = [
            'id', 'requester', 'recipient', 'status',
            'due_date', 'submitted_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'submitted_at']


class FeedbackResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for FeedbackResponse model.
    
    Handles the actual feedback content and ratings.
    """
    
    request_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = FeedbackResponse
        fields = [
            'id', 'request', 'overall_rating', 'strengths',
            'areas_for_improvement', 'specific_examples',
            'recommendations', 'additional_comments',
            'is_anonymous', 'request_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FeedbackTemplateSerializer(serializers.ModelSerializer):
    """
    Serializer for FeedbackTemplate model.
    
    Manages feedback templates with questions and structure.
    """
    
    class Meta:
        model = FeedbackTemplate
        fields = [
            'id', 'name', 'description', 'questions',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FeedbackTemplateListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing feedback templates.
    """
    
    class Meta:
        model = FeedbackTemplate
        fields = ['id', 'name', 'description', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class ManagerFeedbackSerializer(serializers.ModelSerializer):
    """
    Serializer for ManagerFeedback model.
    
    Handles manager-to-employee continuous feedback.
    """
    
    manager = UserListSerializer(read_only=True)
    employee = UserListSerializer(read_only=True)
    employee_id = serializers.IntegerField(write_only=True)
    cycle_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    manager_name = serializers.SerializerMethodField()
    employee_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ManagerFeedback
        fields = [
            'id', 'manager', 'employee', 'cycle', 'feedback_type',
            'subject', 'feedback', 'strengths', 'areas_for_improvement',
            'action_items', 'visibility', 'is_acknowledged',
            'acknowledged_at', 'employee_response',
            'employee_id', 'cycle_id', 'manager_name', 'employee_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'manager', 'created_at', 'updated_at',
            'is_acknowledged', 'acknowledged_at'
        ]
    
    def get_manager_name(self, obj):
        """Get manager's full name."""
        return obj.manager.get_full_name() if obj.manager else 'N/A'
    
    def get_employee_name(self, obj):
        """Get employee's full name."""
        return obj.employee.get_full_name() if obj.employee else 'N/A'
    
    def validate(self, data):
        """Validate manager feedback data."""
        # Get manager from request context
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError('User must be authenticated')
        
        # Get employee from data
        employee_id = data.get('employee_id')
        if not employee_id:
            raise serializers.ValidationError({'employee_id': 'Employee is required'})
        
        # Import User model here to avoid circular import
        from apps.accounts.models import User
        
        try:
            employee = User.objects.get(id=employee_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({'employee_id': 'Employee not found'})
        
        # Validate that the request user is the employee's manager
        if employee.manager != request.user:
            raise serializers.ValidationError({
                'employee_id': 'You can only provide feedback to your direct reports.'
            })
        
        return data
    
    def create(self, validated_data):
        """Create feedback and set manager to current user."""
        request = self.context.get('request')
        validated_data['manager'] = request.user
        
        # Remove write-only fields and get actual objects
        employee_id = validated_data.pop('employee_id')
        cycle_id = validated_data.pop('cycle_id', None)
        
        from apps.accounts.models import User
        from apps.cycles.models import ReviewCycle
        
        validated_data['employee'] = User.objects.get(id=employee_id)
        if cycle_id:
            validated_data['cycle'] = ReviewCycle.objects.get(id=cycle_id)
        
        return super().create(validated_data)


class ManagerFeedbackListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing manager feedback.
    """
    
    manager_name = serializers.SerializerMethodField()
    employee_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ManagerFeedback
        fields = [
            'id', 'manager_name', 'employee_name', 'feedback_type',
            'subject', 'is_acknowledged', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_manager_name(self, obj):
        """Get manager's full name."""
        return obj.manager.get_full_name() if obj.manager else 'N/A'
    
    def get_employee_name(self, obj):
        """Get employee's full name."""
        return obj.employee.get_full_name() if obj.employee else 'N/A'

