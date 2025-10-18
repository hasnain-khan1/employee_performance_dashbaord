"""
Serializers for the reviews app.

This module contains serializers for self-review and manager review management,
including structured content, evidence linking, and audit trails.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    SelfReview, ManagerReview, ReviewAttachment, ReviewAuditTrail,
    SelfReviewSection, EvidenceLink, SelfReviewDraft, SelfReviewAuditTrail,
    SelfReviewTemplate
)
from apps.accounts.serializers import UserListSerializer
from apps.cycles.models import ReviewCycle

User = get_user_model()


class ReviewCycleListSerializer(serializers.ModelSerializer):
    """Simple serializer for ReviewCycle in lists."""
    
    class Meta:
        model = ReviewCycle
        fields = ['id', 'name', 'start_date', 'end_date', 'status']


class SelfReviewSectionSerializer(serializers.ModelSerializer):
    """Serializer for self-review sections."""
    
    class Meta:
        model = SelfReviewSection
        fields = [
            'id', 'section_type', 'content', 'word_count', 'is_completed',
            'min_words', 'max_words', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'word_count', 'created_at', 'updated_at']


class EvidenceLinkSerializer(serializers.ModelSerializer):
    """Serializer for evidence links."""
    
    class Meta:
        model = EvidenceLink
        fields = [
            'id', 'link_type', 'title', 'reference_id', 'url',
            'file_attachment', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SelfReviewSerializer(serializers.ModelSerializer):
    """Serializer for self-reviews."""
    
    employee = UserListSerializer(read_only=True)
    sections = SelfReviewSectionSerializer(many=True, read_only=True)
    evidence_links = EvidenceLinkSerializer(many=True, read_only=True)
    
    class Meta:
        model = SelfReview
        fields = [
            'id', 'employee', 'cycle', 'goal_achievement_summary',
            'key_accomplishments', 'behavioral_competencies', 'development_areas',
            'career_aspirations', 'status', 'completion_percentage',
            'goals_approved', 'peer_feedback_received', 'prerequisites_met',
            'sections', 'evidence_links', 'created_at', 'updated_at',
            'submitted_at', 'last_auto_save'
        ]
        read_only_fields = [
            'id', 'employee', 'completion_percentage', 'created_at',
            'updated_at', 'submitted_at', 'last_auto_save'
        ]


class SelfReviewListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing self-reviews."""
    
    employee = UserListSerializer(read_only=True)
    
    class Meta:
        model = SelfReview
        fields = [
            'id', 'employee', 'cycle', 'status', 'completion_percentage',
            'prerequisites_met', 'created_at', 'submitted_at'
        ]
        read_only_fields = ['id', 'created_at', 'submitted_at']


class SelfReviewDraftSerializer(serializers.ModelSerializer):
    """Serializer for self-review drafts."""
    
    class Meta:
        model = SelfReviewDraft
        fields = [
            'id', 'section_type', 'content', 'word_count',
            'is_auto_save', 'save_reason', 'created_at'
        ]
        read_only_fields = ['id', 'word_count', 'created_at']


class SelfReviewAuditTrailSerializer(serializers.ModelSerializer):
    """Serializer for self-review audit trail."""
    
    user = UserListSerializer(read_only=True)
    
    class Meta:
        model = SelfReviewAuditTrail
        fields = [
            'id', 'action', 'section_type', 'changes_summary',
            'previous_content', 'new_content', 'user', 'timestamp',
            'ip_address', 'user_agent'
        ]
        read_only_fields = ['id', 'timestamp']


class SelfReviewTemplateSerializer(serializers.ModelSerializer):
    """Serializer for self-review templates."""
    
    created_by = UserListSerializer(read_only=True)
    
    class Meta:
        model = SelfReviewTemplate
        fields = [
            'id', 'name', 'description', 'sections_config',
            'writing_guidelines', 'examples', 'is_active',
            'is_default', 'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReviewAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for review attachments."""
    
    uploaded_by = UserListSerializer(read_only=True)
    
    class Meta:
        model = ReviewAttachment
        fields = [
            'id', 'file', 'file_name', 'file_size', 'file_type',
            'description', 'uploaded_by', 'uploaded_at'
        ]
        read_only_fields = ['id', 'file_size', 'uploaded_at']


class ReviewAuditTrailSerializer(serializers.ModelSerializer):
    """Serializer for review audit trail."""
    
    user = UserListSerializer(read_only=True)
    
    class Meta:
        model = ReviewAuditTrail
        fields = [
            'id', 'action', 'field_changed', 'old_value', 'new_value',
            'change_summary', 'user', 'timestamp', 'ip_address', 'user_agent'
        ]
        read_only_fields = ['id', 'timestamp']


class ManagerReviewSerializer(serializers.ModelSerializer):
    """Serializer for manager reviews."""
    
    employee = UserListSerializer(read_only=True)
    manager = UserListSerializer(read_only=True)
    cycle = ReviewCycleListSerializer(read_only=True)
    attachments = ReviewAttachmentSerializer(many=True, read_only=True)
    audit_trail = ReviewAuditTrailSerializer(many=True, read_only=True)
    
    # Computed fields
    average_competency_rating = serializers.ReadOnlyField()
    is_complete = serializers.ReadOnlyField()
    
    class Meta:
        model = ManagerReview
        fields = [
            'id', 'employee', 'manager', 'cycle', 'review_period_start',
            'review_period_end', 'goals_achievements', 'communication_rating',
            'collaboration_rating', 'leadership_rating', 'problem_solving_rating',
            'adaptability_rating', 'overall_rating', 'performance_summary',
            'strengths', 'development_areas', 'career_recommendations',
            'comments', 'private_notes', 'development_notes', 'status',
            'is_locked', 'average_competency_rating', 'is_complete',
            'attachments', 'audit_trail', 'created_at', 'updated_at',
            'submitted_at', 'approved_at', 'last_auto_save'
        ]
        read_only_fields = [
            'id', 'manager', 'average_competency_rating', 'is_complete',
            'created_at', 'updated_at', 'submitted_at', 'approved_at',
            'last_auto_save'
        ]
    
    def validate(self, data):
        """Validate review data."""
        # Validate review period dates
        if 'review_period_start' in data and 'review_period_end' in data:
            if data['review_period_end'] <= data['review_period_start']:
                raise serializers.ValidationError(
                    "End date must be after start date."
                )
        
        # Validate rating ranges
        rating_fields = [
            'communication_rating', 'collaboration_rating', 'leadership_rating',
            'problem_solving_rating', 'adaptability_rating', 'overall_rating'
        ]
        
        for field in rating_fields:
            if field in data and data[field] is not None:
                if not (1 <= data[field] <= 5):
                    raise serializers.ValidationError(
                        f"{field.replace('_', ' ').title()} must be between 1 and 5."
                    )
        
        # Validate comments length
        if 'comments' in data and len(data['comments']) > 5000:
            raise serializers.ValidationError(
                "Comments cannot exceed 5,000 characters."
            )
        
        return data


class ManagerReviewListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing manager reviews."""
    
    employee = UserListSerializer(read_only=True)
    manager = UserListSerializer(read_only=True)
    average_competency_rating = serializers.ReadOnlyField()
    
    class Meta:
        model = ManagerReview
        fields = [
            'id', 'employee', 'manager', 'cycle', 'review_period_start',
            'review_period_end', 'overall_rating', 'average_competency_rating',
            'status', 'is_locked', 'created_at', 'submitted_at'
        ]
        read_only_fields = ['id', 'created_at', 'submitted_at']


class ManagerReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating manager reviews."""
    
    class Meta:
        model = ManagerReview
        fields = [
            'employee', 'cycle', 'review_period_start', 'review_period_end',
            'goals_achievements', 'communication_rating', 'collaboration_rating',
            'leadership_rating', 'problem_solving_rating', 'adaptability_rating',
            'overall_rating', 'performance_summary', 'strengths',
            'development_areas', 'career_recommendations', 'comments',
            'private_notes', 'development_notes'
        ]
    
    def validate_employee(self, value):
        """Validate that the employee is a direct report."""
        manager = self.context['request'].user
        if not manager.is_manager:
            raise serializers.ValidationError(
                "Only managers can create reviews."
            )
        
        # Check if employee is a direct report
        if value.manager != manager:
            raise serializers.ValidationError(
                "You can only review your direct reports."
            )
        
        return value
    
    def create(self, validated_data):
        """Create manager review with audit trail."""
        validated_data['manager'] = self.context['request'].user
        
        # Create the review
        review = super().create(validated_data)
        
        # Create audit trail entry
        ReviewAuditTrail.objects.create(
            manager_review=review,
            action='created',
            user=self.context['request'].user,
            change_summary='Manager review created',
            ip_address=self.context['request'].META.get('REMOTE_ADDR'),
            user_agent=self.context['request'].META.get('HTTP_USER_AGENT', '')
        )
        
        return review


class ManagerReviewUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating manager reviews."""
    
    class Meta:
        model = ManagerReview
        fields = [
            'goals_achievements', 'communication_rating', 'collaboration_rating',
            'leadership_rating', 'problem_solving_rating', 'adaptability_rating',
            'overall_rating', 'performance_summary', 'strengths',
            'development_areas', 'career_recommendations', 'comments',
            'private_notes', 'development_notes'
        ]
    
    def update(self, instance, validated_data):
        """Update manager review with audit trail."""
        # Track changes for audit trail
        changes = []
        for field, value in validated_data.items():
            if hasattr(instance, field):
                old_value = getattr(instance, field)
                if old_value != value:
                    changes.append(f"{field}: {old_value} -> {value}")
        
        # Update the instance
        updated_instance = super().update(instance, validated_data)
        
        # Create audit trail entry if there were changes
        if changes:
            ReviewAuditTrail.objects.create(
                manager_review=updated_instance,
                action='updated',
                user=self.context['request'].user,
                change_summary='; '.join(changes),
                ip_address=self.context['request'].META.get('REMOTE_ADDR'),
                user_agent=self.context['request'].META.get('HTTP_USER_AGENT', '')
            )
        
        return updated_instance


class ManagerReviewSubmitSerializer(serializers.Serializer):
    """Serializer for submitting manager reviews."""
    
    def validate(self, data):
        """Validate that review is complete before submission."""
        review = self.context['review']
        
        # Check if all required sections are completed
        required_sections = [
            review.performance_summary,
            review.strengths,
            review.development_areas,
            review.career_recommendations
        ]
        
        if not all(section.strip() for section in required_sections):
            raise serializers.ValidationError(
                "All required narrative sections must be completed."
            )
        
        if review.overall_rating is None:
            raise serializers.ValidationError(
                "Overall rating is required."
            )
        
        # Check word count requirements for narrative sections
        min_words = 200
        for section in required_sections:
            if len(section.split()) < min_words:
                raise serializers.ValidationError(
                    f"Manager narrative section incomplete - minimum {min_words} words required."
                )
        
        return data


class ManagerReviewBulkActionSerializer(serializers.Serializer):
    """Serializer for bulk actions on manager reviews."""
    
    review_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of review IDs to perform action on"
    )
    action = serializers.ChoiceField(
        choices=['submit', 'approve', 'return', 'lock', 'unlock'],
        help_text="Action to perform on selected reviews"
    )
    reason = serializers.CharField(
        required=False,
        help_text="Reason for the action"
    )
    
    def validate_review_ids(self, value):
        """Validate that all review IDs exist and are accessible."""
        manager = self.context['request'].user
        reviews = ManagerReview.objects.filter(
            id__in=value,
            manager=manager
        )
        
        if len(reviews) != len(value):
            raise serializers.ValidationError(
                "Some review IDs are invalid or not accessible."
            )
        
        return value