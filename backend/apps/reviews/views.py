"""
Views for the reviews app.

This module contains views for self-review and manager review management,
including comprehensive performance evaluation capabilities.
"""

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiTypes
from drf_spectacular.types import OpenApiTypes

from .models import (
    SelfReview, ManagerReview, ReviewAttachment, ReviewAuditTrail,
    SelfReviewSection, EvidenceLink, SelfReviewDraft, SelfReviewAuditTrail,
    SelfReviewTemplate
)
from .serializers import (
    SelfReviewSerializer, SelfReviewListSerializer, SelfReviewSectionSerializer,
    EvidenceLinkSerializer, SelfReviewDraftSerializer, SelfReviewAuditTrailSerializer,
    SelfReviewTemplateSerializer, ManagerReviewSerializer, ManagerReviewListSerializer,
    ManagerReviewCreateSerializer, ManagerReviewUpdateSerializer,
    ManagerReviewSubmitSerializer, ManagerReviewBulkActionSerializer,
    ReviewAttachmentSerializer, ReviewAuditTrailSerializer
)
from apps.accounts.models import User
from apps.cycles.models import ReviewCycle


# Root Reviews View
class ReviewsListView(generics.ListAPIView):
    """List all reviews based on user role and view parameter."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        view_type = self.request.query_params.get('view', 'all')
        
        if view_type == 'reviewer':
            return ManagerReviewListSerializer
        else:
            # Default to self-reviews for backward compatibility
            return SelfReviewListSerializer
    
    def get_queryset(self):
        user = self.request.user
        view_type = self.request.query_params.get('view', 'all')
        
        if view_type == 'reviewer':
            # Return manager reviews where user is the reviewer
            if user.is_hr:
                # HR can see all manager reviews
                queryset = ManagerReview.objects.all()
            elif user.is_manager:
                # Managers can see their own reviews
                queryset = ManagerReview.objects.filter(manager=user)
            else:
                # Employees can see reviews about them
                queryset = ManagerReview.objects.filter(employee=user)
        else:
            # Default to self-reviews
            queryset = SelfReview.objects.filter(employee=user)
        
        # Apply additional filters
        cycle_id = self.request.query_params.get('cycle')
        if cycle_id:
            queryset = queryset.filter(cycle_id=cycle_id)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        search_query = self.request.query_params.get('search')
        if search_query:
            if view_type == 'reviewer':
                queryset = queryset.filter(
                    Q(employee__first_name__icontains=search_query) |
                    Q(employee__last_name__icontains=search_query) |
                    Q(employee__email__icontains=search_query)
                )
            else:
                queryset = queryset.filter(
                    Q(goal_achievement_summary__icontains=search_query) |
                    Q(key_accomplishments__icontains=search_query)
                )
        
        return queryset.order_by('-created_at')


# Self-Review Views
class SelfReviewListView(generics.ListCreateAPIView):
    """List and create self-reviews."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SelfReviewListSerializer
        return SelfReviewSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = SelfReview.objects.filter(employee=user)
        
        # Filter by cycle if provided
        cycle_id = self.request.query_params.get('cycle')
        if cycle_id:
            queryset = queryset.filter(cycle_id=cycle_id)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(employee=self.request.user)


class SelfReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a self-review."""
    
    serializer_class = SelfReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return SelfReview.objects.filter(employee=user)


class SelfReviewSectionListView(generics.ListCreateAPIView):
    """List and create self-review sections."""
    
    serializer_class = SelfReviewSectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        self_review_id = self.kwargs.get('self_review_id')
        return SelfReviewSection.objects.filter(
            self_review__employee=user,
            self_review_id=self_review_id
        )
    
    def perform_create(self, serializer):
        self_review_id = self.kwargs.get('self_review_id')
        self_review = get_object_or_404(
            SelfReview,
            id=self_review_id,
            employee=self.request.user
        )
        serializer.save(self_review=self_review)


class SelfReviewSectionView(generics.RetrieveUpdateAPIView):
    """Update a specific self-review section."""
    
    serializer_class = SelfReviewSectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return SelfReviewSection.objects.filter(self_review__employee=user)


class EvidenceLinkView(generics.ListCreateAPIView):
    """List and create evidence links for self-reviews."""
    
    serializer_class = EvidenceLinkSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        self_review_id = self.kwargs.get('self_review_id')
        return EvidenceLink.objects.filter(
            self_review__employee=user,
            self_review_id=self_review_id
        )
    
    def perform_create(self, serializer):
        self_review_id = self.kwargs.get('self_review_id')
        self_review = get_object_or_404(
            SelfReview,
            id=self_review_id,
            employee=self.request.user
        )
        serializer.save(self_review=self_review)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="Get Current Self-Review",
    description="Get the current active self-review for the logged-in user.",
    responses={
        200: SelfReviewSerializer,
        400: "No active review cycle found or no current self-review found",
        401: "Authentication required"
    }
)
def get_current_self_review(request):
    """Get the current active self-review for the user."""
    try:
        # Get the current active review cycle
        current_cycle = ReviewCycle.objects.filter(is_active=True).first()
        
        if not current_cycle:
            return Response(
                {'error': 'No active review cycle found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the current self-review for the user in the active cycle
        self_review = SelfReview.objects.filter(
            employee=request.user,
            cycle=current_cycle
        ).first()
        
        if not self_review:
            return Response(
                {'error': 'No current self-review found for this cycle'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = SelfReviewSerializer(self_review, context={'request': request})
        return Response(serializer.data)
        
    except Exception as e:
        return Response(
            {'error': f'Error retrieving current self-review: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="Check Self-Review Prerequisites",
    description="Check if the user meets prerequisites for self-review.",
    responses={
        200: "Prerequisites check completed",
        401: "Authentication required"
    }
)
def check_self_review_prerequisites(request):
    """Check if the user meets prerequisites for self-review."""
    try:
        # Get the current active review cycle
        current_cycle = ReviewCycle.objects.filter(is_active=True).first()
        
        if not current_cycle:
            return Response({
                'can_review': False,
                'reason': 'No active review cycle found',
                'cycle_active': False
            })
        
        # Check if user has goals for this cycle
        from apps.goals.models import Goal
        user_goals = Goal.objects.filter(
            employee=request.user,
            cycle=current_cycle
        ).exclude(status='cancelled')
        
        has_goals = user_goals.exists()
        has_approved_goals = user_goals.filter(status='approved').exists()
        
        # Check if user already has a self-review for this cycle
        existing_review = SelfReview.objects.filter(
            employee=request.user,
            cycle=current_cycle
        ).first()
        
        return Response({
            'can_review': has_goals and has_approved_goals,
            'has_goals': has_goals,
            'has_approved_goals': has_approved_goals,
            'goals_count': user_goals.count(),
            'approved_goals_count': user_goals.filter(status='approved').count(),
            'has_existing_review': existing_review is not None,
            'cycle_active': True,
            'cycle_name': current_cycle.name,
            'cycle_period': f"{current_cycle.start_date} to {current_cycle.end_date}"
        })
        
    except Exception as e:
        return Response(
            {'error': f'Error checking prerequisites: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="Submit Self-Review",
    description="Submit a completed self-review for manager review.",
    responses={
        200: "Self-review submitted successfully",
        400: "Validation error",
        401: "Authentication required"
    }
)
def submit_self_review(request, pk):
    """Submit a self-review for manager review."""
    try:
        self_review = get_object_or_404(
            SelfReview,
            pk=pk,
            employee=request.user
        )
        
        # Validate prerequisites
        if not self_review.prerequisites_met:
            return Response(
                {'error': 'Prerequisites not met. Please complete goals and peer feedback first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate completion
        if self_review.completion_percentage < 100:
            return Response(
                {'error': 'Self-review must be 100% complete before submission.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update status
        self_review.status = 'submitted'
        self_review.submitted_at = timezone.now()
        self_review.save()
        
        # Create audit trail entry
        SelfReviewAuditTrail.objects.create(
            self_review=self_review,
            action='submitted',
            user=request.user,
            changes_summary='Self-review submitted for manager review',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({'message': 'Self-review submitted successfully'})
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="Auto-save Self-Review",
    description="Auto-save self-review content to prevent data loss.",
    responses={
        200: "Auto-save successful",
        400: "Validation error"
    }
)
def auto_save_self_review(request, pk):
    """Auto-save self-review content."""
    try:
        self_review = get_object_or_404(
            SelfReview,
            pk=pk,
            employee=request.user
        )
        
        # Update content fields
        content_fields = [
            'goal_achievement_summary', 'key_accomplishments',
            'behavioral_competencies', 'development_areas', 'career_aspirations'
        ]
        
        for field in content_fields:
            if field in request.data:
                setattr(self_review, field, request.data[field])
        
        self_review.last_auto_save = timezone.now()
        self_review.save()
        
        # Create draft entry
        section_type = request.data.get('section_type', 'general')
        content = request.data.get('content', '')
        
        SelfReviewDraft.objects.create(
            self_review=self_review,
            section_type=section_type,
            content=content,
            word_count=len(content.split()) if content else 0,
            is_auto_save=True,
            save_reason='auto_save'
        )
        
        return Response({'message': 'Auto-save successful'})
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Manager Review Views
class ManagerReviewListView(generics.ListCreateAPIView):
    """List and create manager reviews."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ManagerReviewListSerializer
        return ManagerReviewCreateSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_hr:
            # HR can see all reviews
            queryset = ManagerReview.objects.all()
        elif user.is_manager:
            # Managers can see their own reviews
            queryset = ManagerReview.objects.filter(manager=user)
        else:
            # Employees can see reviews about them
            queryset = ManagerReview.objects.filter(employee=user)
        
        # Filter by cycle if provided
        cycle_id = self.request.query_params.get('cycle')
        if cycle_id:
            queryset = queryset.filter(cycle_id=cycle_id)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(manager=self.request.user)


class ManagerReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a manager review."""
    
    serializer_class = ManagerReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_hr:
            return ManagerReview.objects.all()
        elif user.is_manager:
            return ManagerReview.objects.filter(manager=user)
        else:
            return ManagerReview.objects.filter(employee=user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="Get Employee Dossier",
    description="Get comprehensive employee performance dossier for manager review.",
    responses={
        200: OpenApiTypes.OBJECT,
        401: "Authentication required",
        403: "Access denied",
        404: "Employee not found"
    }
)
def get_employee_dossier(request, employee_id):
    """Get comprehensive employee performance dossier."""
    try:
        manager = request.user
        
        # Validate manager permissions
        if not manager.is_manager:
            return Response(
                {'error': 'Access denied - manager role required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get employee
        employee = get_object_or_404(User, id=employee_id)
        
        # Check if employee is a direct report
        if employee.manager != manager:
            return Response(
                {'error': 'Access denied - not your direct report'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get active cycle
        cycle = ReviewCycle.objects.filter(is_active=True).first()
        if not cycle:
            return Response(
                {'error': 'No active review cycle found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get employee data
        dossier = {
            'employee': {
                'id': employee.id,
                'name': employee.get_full_name(),
                'email': employee.email,
                'department': employee.department.name if employee.department else None,
                'position': employee.job_title,
                'hire_date': employee.date_joined
            },
            'cycle': {
                'id': cycle.id,
                'name': cycle.name,
                'start_date': cycle.start_date,
                'end_date': cycle.end_date
            },
            'goals': [],
            'self_review': None,
            'peer_feedback': [],
            'manager_review': None,
            'performance_metrics': {}
        }
        
        # Get goals
        from apps.goals.models import Goal
        goals = Goal.objects.filter(employee=employee, cycle=cycle)
        for goal in goals:
            dossier['goals'].append({
                'id': goal.id,
                'title': goal.title,
                'status': goal.status,
                'progress_percentage': goal.progress_percentage,
                'target_date': goal.target_date,
                'priority': goal.priority
            })
        
        # Get self-review
        try:
            self_review = SelfReview.objects.get(employee=employee, cycle=cycle)
            dossier['self_review'] = {
                'id': self_review.id,
                'status': self_review.status,
                'completion_percentage': self_review.completion_percentage,
                'submitted_at': self_review.submitted_at
            }
        except SelfReview.DoesNotExist:
            pass
        
        # Get peer feedback
        from apps.feedback.models import FeedbackRequest
        feedback_requests = FeedbackRequest.objects.filter(
            requester=employee,
            cycle=cycle
        )
        for request in feedback_requests:
            dossier['peer_feedback'].append({
                'id': request.id,
                'title': request.title,
                'status': request.status,
                'completion_percentage': request.completion_percentage
            })
        
        # Get existing manager review
        try:
            manager_review = ManagerReview.objects.get(
                employee=employee,
                manager=manager,
                cycle=cycle
            )
            dossier['manager_review'] = {
                'id': manager_review.id,
                'status': manager_review.status,
                'overall_rating': manager_review.overall_rating,
                'is_locked': manager_review.is_locked
            }
        except ManagerReview.DoesNotExist:
            pass
        
        return Response(dossier)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="Submit Manager Review",
    description="Submit a completed manager review with final rating.",
    responses={
        200: "Manager review submitted successfully",
        400: "Validation error",
        401: "Authentication required",
        403: "Access denied"
    }
)
def submit_manager_review(request, pk):
    """Submit a manager review."""
    try:
        manager_review = get_object_or_404(
            ManagerReview,
            pk=pk,
            manager=request.user
        )
        
        # Validate review is complete
        if not manager_review.is_complete:
            return Response(
                {'error': 'All required sections must be completed before submission.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate narrative word counts
        min_words = 200
        narrative_sections = [
            manager_review.performance_summary,
            manager_review.strengths,
            manager_review.development_areas,
            manager_review.career_recommendations
        ]
        
        for i, section in enumerate(narrative_sections):
            if len(section.split()) < min_words:
                section_names = ['performance_summary', 'strengths', 'development_areas', 'career_recommendations']
                return Response(
                    {'error': f'Manager narrative section "{section_names[i]}" incomplete - minimum {min_words} words required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Update status and lock
        manager_review.status = 'submitted'
        manager_review.is_locked = True
        manager_review.submitted_at = timezone.now()
        manager_review.save()
        
        # Create audit trail entry
        ReviewAuditTrail.objects.create(
            manager_review=manager_review,
            action='submitted',
            user=request.user,
            change_summary='Manager review submitted and locked',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({'message': 'Manager review submitted successfully'})
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="Upload Review Attachment",
    description="Upload an attachment for a manager review.",
    responses={
        201: ReviewAttachmentSerializer,
        400: "Validation error",
        401: "Authentication required"
    }
)
def upload_review_attachment(request, review_id):
    """Upload an attachment for a manager review."""
    try:
        manager_review = get_object_or_404(
            ManagerReview,
            pk=review_id,
            manager=request.user
        )
        
        # Validate file size (10MB limit)
        file = request.FILES.get('file')
        if file and file.size > 10 * 1024 * 1024:  # 10MB
            return Response(
                {'error': 'Attachment exceeds 10MB'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create attachment
        attachment = ReviewAttachment.objects.create(
            manager_review=manager_review,
            file=file,
            file_name=file.name if file else '',
            file_size=file.size if file else 0,
            file_type=request.data.get('file_type', 'document'),
            description=request.data.get('description', ''),
            uploaded_by=request.user
        )
        
        serializer = ReviewAttachmentSerializer(attachment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="Bulk Action on Reviews",
    description="Perform bulk actions on multiple manager reviews.",
    responses={
        200: "Bulk action completed successfully",
        400: "Validation error",
        401: "Authentication required"
    }
)
def bulk_review_action(request):
    """Perform bulk actions on manager reviews."""
    try:
        serializer = ManagerReviewBulkActionSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        review_ids = serializer.validated_data['review_ids']
        action = serializer.validated_data['action']
        reason = serializer.validated_data.get('reason', '')
        
        # Get reviews
        reviews = ManagerReview.objects.filter(
            id__in=review_ids,
            manager=request.user
        )
        
        # Perform action
        updated_count = 0
        for review in reviews:
            if action == 'submit':
                if not review.is_locked:
                    review.status = 'submitted'
                    review.is_locked = True
                    review.submitted_at = timezone.now()
                    review.save()
                    updated_count += 1
            elif action == 'approve':
                if review.status == 'submitted':
                    review.status = 'approved'
                    review.approved_at = timezone.now()
                    review.save()
                    updated_count += 1
            elif action == 'return':
                if review.status in ['submitted', 'approved']:
                    review.status = 'returned'
                    review.is_locked = False
                    review.save()
                    updated_count += 1
            elif action == 'lock':
                if not review.is_locked:
                    review.is_locked = True
                    review.save()
                    updated_count += 1
            elif action == 'unlock':
                if review.is_locked:
                    review.is_locked = False
                    review.save()
                    updated_count += 1
        
        return Response({
            'message': f'Bulk action completed. {updated_count} reviews updated.',
            'action': action,
            'updated_count': updated_count
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="Get Review Statistics",
    description="Get statistics for manager reviews.",
    responses={
        200: OpenApiTypes.OBJECT,
        401: "Authentication required"
    }
)
def get_review_statistics(request):
    """Get statistics for manager reviews."""
    try:
        user = request.user
        
        if user.is_hr:
            # HR statistics
            stats = {
                'total_reviews': ManagerReview.objects.count(),
                'submitted_reviews': ManagerReview.objects.filter(status='submitted').count(),
                'approved_reviews': ManagerReview.objects.filter(status='approved').count(),
                'draft_reviews': ManagerReview.objects.filter(status='draft').count(),
                'locked_reviews': ManagerReview.objects.filter(is_locked=True).count()
            }
        elif user.is_manager:
            # Manager statistics
            stats = {
                'my_reviews': ManagerReview.objects.filter(manager=user).count(),
                'submitted_reviews': ManagerReview.objects.filter(
                    manager=user, status='submitted'
                ).count(),
                'approved_reviews': ManagerReview.objects.filter(
                    manager=user, status='approved'
                ).count(),
                'draft_reviews': ManagerReview.objects.filter(
                    manager=user, status='draft'
                ).count(),
                'direct_reports_count': User.objects.filter(manager=user).count()
            }
        else:
            # Employee statistics
            stats = {
                'reviews_about_me': ManagerReview.objects.filter(employee=user).count(),
                'pending_reviews': ManagerReview.objects.filter(
                    employee=user, status='draft'
                ).count(),
                'completed_reviews': ManagerReview.objects.filter(
                    employee=user, status__in=['submitted', 'approved']
                ).count()
            }
        
        return Response(stats)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Template Views
class SelfReviewTemplateListView(generics.ListAPIView):
    """List self-review templates."""
    
    serializer_class = SelfReviewTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SelfReviewTemplate.objects.filter(is_active=True)


class SelfReviewTemplateDetailView(generics.RetrieveAPIView):
    """Retrieve a self-review template."""
    
    serializer_class = SelfReviewTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = SelfReviewTemplate.objects.filter(is_active=True)