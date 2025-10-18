"""
Serializers for the feedback app.

This module contains serializers for peer feedback system including
requests, responses, templates, and content policy enforcement.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    FeedbackRequest, FeedbackResponse, FeedbackTemplate,
    PeerReviewer, ContentPolicyRule
)

User = get_user_model()


class UserListSerializer(serializers.ModelSerializer):
    """Serializer for user list display."""
    
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'department', 'avatar']
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class FeedbackRequestSerializer(serializers.ModelSerializer):
    """Serializer for feedback requests."""
    
    requester = UserListSerializer(read_only=True)
    requester_id = serializers.IntegerField(write_only=True, required=False)
    cycle_id = serializers.IntegerField(write_only=True, required=False)
    peer_reviewers = serializers.SerializerMethodField()
    completion_percentage = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = FeedbackRequest
        fields = [
            'id', 'requester', 'requester_id', 'cycle', 'cycle_id',
            'title', 'description', 'deadline', 'status',
            'allow_anonymous', 'min_peers', 'max_peers',
            'completion_percentage', 'is_expired', 'peer_reviewers',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'completion_percentage', 'is_expired']
    
    def get_peer_reviewers(self, obj):
        """Get peer reviewers for this request."""
        return PeerReviewerSerializer(obj.peer_reviewers.all(), many=True).data
    
    def create(self, validated_data):
        """Create feedback request with auto-assigned requester."""
        validated_data.pop('requester_id', None)
        validated_data.pop('cycle_id', None)
        return super().create(validated_data)


class PeerReviewerSerializer(serializers.ModelSerializer):
    """Serializer for peer reviewers."""
    
    reviewer = UserListSerializer(read_only=True)
    reviewer_id = serializers.IntegerField(write_only=True, required=False)
    feedback_request_id = serializers.IntegerField(write_only=True, required=False)
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = PeerReviewer
        fields = [
            'id', 'reviewer', 'reviewer_id', 'feedback_request', 'feedback_request_id',
            'relationship_context', 'personal_message', 'status',
            'invited_at', 'responded_at', 'reminder_sent_count',
            'last_reminder_sent', 'is_overdue'
        ]
        read_only_fields = ['id', 'invited_at', 'responded_at', 'reminder_sent_count', 'last_reminder_sent', 'is_overdue']
    
    def create(self, validated_data):
        """Create peer reviewer with auto-assigned relationships."""
        validated_data.pop('reviewer_id', None)
        validated_data.pop('feedback_request_id', None)
        return super().create(validated_data)


class FeedbackResponseSerializer(serializers.ModelSerializer):
    """Serializer for feedback responses."""
    
    peer_reviewer = PeerReviewerSerializer(read_only=True)
    peer_reviewer_id = serializers.IntegerField(write_only=True, required=False)
    average_rating = serializers.ReadOnlyField()
    
    class Meta:
        model = FeedbackResponse
        fields = [
            'id', 'peer_reviewer', 'peer_reviewer_id', 'is_submitted', 'is_anonymous',
            'communication_rating', 'collaboration_rating', 'leadership_rating',
            'problem_solving_rating', 'adaptability_rating', 'overall_rating',
            'strengths', 'development_areas', 'collaboration_examples',
            'additional_comments', 'content_policy_violations', 'content_policy_approved',
            'average_rating', 'created_at', 'updated_at', 'submitted_at'
        ]
        read_only_fields = [
            'id', 'content_policy_violations', 'content_policy_approved',
            'average_rating', 'created_at', 'updated_at', 'submitted_at'
        ]
    
    def create(self, validated_data):
        """Create feedback response with auto-assigned peer reviewer."""
        validated_data.pop('peer_reviewer_id', None)
        return super().create(validated_data)


class FeedbackTemplateSerializer(serializers.ModelSerializer):
    """Serializer for feedback templates."""
    
    created_by = UserListSerializer(read_only=True)
    created_by_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = FeedbackTemplate
        fields = [
            'id', 'name', 'description', 'competencies', 'questions',
            'rating_scale', 'is_active', 'is_default', 'created_by',
            'created_by_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Create feedback template with auto-assigned creator."""
        validated_data.pop('created_by_id', None)
        return super().create(validated_data)


class ContentPolicyRuleSerializer(serializers.ModelSerializer):
    """Serializer for content policy rules."""
    
    created_by = UserListSerializer(read_only=True)
    created_by_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = ContentPolicyRule
        fields = [
            'id', 'name', 'rule_type', 'severity', 'keywords', 'patterns',
            'min_length', 'max_length', 'is_active', 'auto_block',
            'warning_message', 'created_by', 'created_by_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Create content policy rule with auto-assigned creator."""
        validated_data.pop('created_by_id', None)
        return super().create(validated_data)


class FeedbackRequestListSerializer(serializers.ModelSerializer):
    """Simplified serializer for feedback request lists."""
    
    requester = UserListSerializer(read_only=True)
    completion_percentage = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    peer_count = serializers.SerializerMethodField()
    
    class Meta:
        model = FeedbackRequest
        fields = [
            'id', 'title', 'requester', 'deadline', 'status',
            'completion_percentage', 'is_expired', 'peer_count',
            'created_at'
        ]
    
    def get_peer_count(self, obj):
        """Get count of peer reviewers."""
        return obj.peer_reviewers.count()


class FeedbackResponseListSerializer(serializers.ModelSerializer):
    """Simplified serializer for feedback response lists."""
    
    reviewer = UserListSerializer(source='peer_reviewer.reviewer', read_only=True)
    average_rating = serializers.ReadOnlyField()
    
    class Meta:
        model = FeedbackResponse
        fields = [
            'id', 'reviewer', 'is_submitted', 'is_anonymous',
            'overall_rating', 'average_rating', 'submitted_at'
        ]