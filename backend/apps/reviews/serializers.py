"""
Serializers for the reviews app.

This module contains serializers for reviews, review sections,
and review templates.
"""

from rest_framework import serializers
from .models import Review, ReviewSection, ReviewTemplate
from apps.accounts.serializers import UserListSerializer


class ReviewSectionSerializer(serializers.ModelSerializer):
    """
    Serializer for ReviewSection model.
    
    Handles individual review sections with ratings and comments.
    """
    
    class Meta:
        model = ReviewSection
        fields = [
            'id', 'title', 'description', 'rating',
            'comments', 'order'
        ]
        read_only_fields = ['id']


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for Review model.
    
    Provides full review information including sections
    and participant details.
    """
    
    employee = UserListSerializer(read_only=True)
    reviewer = UserListSerializer(read_only=True)
    sections = ReviewSectionSerializer(many=True, read_only=True)
    employee_id = serializers.IntegerField(write_only=True, required=False)
    reviewer_id = serializers.IntegerField(write_only=True, required=False)
    cycle_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'employee', 'reviewer', 'cycle', 'review_type',
            'status', 'overall_rating', 'achievements', 'challenges',
            'development_areas', 'goals_for_next_period', 'comments',
            'sections', 'submitted_at', 'approved_at',
            'employee_id', 'reviewer_id', 'cycle_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at',
            'submitted_at', 'approved_at'
        ]


class ReviewListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing reviews.
    """
    
    employee = UserListSerializer(read_only=True)
    reviewer = UserListSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'employee', 'reviewer', 'review_type',
            'status', 'overall_rating', 'submitted_at',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'submitted_at']


class ReviewTemplateSerializer(serializers.ModelSerializer):
    """
    Serializer for ReviewTemplate model.
    
    Manages review templates with sections and questions.
    """
    
    class Meta:
        model = ReviewTemplate
        fields = [
            'id', 'name', 'description', 'review_type',
            'sections', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReviewTemplateListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing review templates.
    """
    
    class Meta:
        model = ReviewTemplate
        fields = [
            'id', 'name', 'description', 'review_type',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

