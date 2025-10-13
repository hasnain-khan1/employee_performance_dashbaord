"""
Serializers for the feedback app.

This module contains serializers for feedback requests,
responses, and templates.
"""

from rest_framework import serializers
from .models import FeedbackRequest, FeedbackResponse, FeedbackTemplate
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

