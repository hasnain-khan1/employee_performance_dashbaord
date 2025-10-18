"""
Views for the goals app.

This module contains API views for goal management,
including SMART goal creation, tracking, and evaluation.
"""

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db.models import Q
from django.utils import timezone

from .models import Goal, GoalCategory, GoalUpdate
from .serializers import (
    GoalSerializer, GoalListSerializer, GoalCategorySerializer,
    GoalUpdateSerializer
)
from apps.cycles.models import ReviewCycle


class GoalListView(generics.ListCreateAPIView):
    """
    Goal list and creation endpoint.
    
    Provides list of goals with filtering,
    and allows creation of new goals.
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method == 'GET':
            return GoalListSerializer
        return GoalSerializer
    
    def get_queryset(self):
        """Get filtered queryset of goals."""
        user = self.request.user
        queryset = Goal.objects.select_related('employee', 'cycle', 'approved_by')
        
        # Filter by user's goals unless they're a manager/HR
        if not user.is_hr:
            # Show goals where user is the employee or the approver
            queryset = queryset.filter(
                Q(employee=user) | Q(approved_by=user)
            )
        
        # Apply filters
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """
        Create a new goal with auto-assigned employee and cycle.
        """
        # Get or create an active cycle
        cycle = ReviewCycle.objects.filter(is_active=True).first()
        
        if not cycle:
            # Create a default cycle if none exists
            from datetime import datetime, timedelta
            today = datetime.now().date()
            
            cycle = ReviewCycle.objects.create(
                name=f"Performance Cycle {today.year}",
                start_date=today,
                end_date=today + timedelta(days=365),
                goal_setting_start=today,
                goal_setting_end=today + timedelta(days=30),
                self_review_start=today + timedelta(days=300),
                self_review_end=today + timedelta(days=330),
                manager_review_start=today + timedelta(days=330),
                manager_review_end=today + timedelta(days=360),
                is_active=True,
                created_by=self.request.user  # Set creator to current user
            )
        
        serializer.save(
            employee=self.request.user,
            cycle=cycle
        )
    
    @extend_schema(
        summary="List Goals",
        description="Get a list of goals with optional filtering.",
        parameters=[
            OpenApiParameter(
                name='status',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by status'
            ),
            OpenApiParameter(
                name='priority',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by priority'
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search by title or description'
            ),
        ],
        responses={
            200: GoalListSerializer(many=True),
            401: "Authentication required"
        }
    )
    def get(self, request, *args, **kwargs):
        """Get list of goals."""
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create Goal",
        description="Create a new SMART goal.",
        responses={
            201: GoalSerializer,
            400: "Validation error",
            401: "Authentication required"
        }
    )
    def post(self, request, *args, **kwargs):
        """Create a new goal."""
        return super().post(request, *args, **kwargs)


class GoalDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Goal detail endpoint.
    
    Provides detailed information about a specific goal
    and allows updates and deletion.
    """
    
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'
    
    def get_queryset(self):
        """Get queryset filtered by user access."""
        user = self.request.user
        queryset = Goal.objects.select_related('employee', 'cycle', 'approved_by')
        
        # Filter by user's access
        if not user.is_hr:
            # Show goals where user is the employee or the approver
            queryset = queryset.filter(
                Q(employee=user) | Q(approved_by=user)
            )
        
        return queryset
    
    @extend_schema(
        summary="Get Goal Details",
        description="Retrieve detailed information about a specific goal.",
        responses={
            200: GoalSerializer,
            404: "Goal not found",
            401: "Authentication required"
        }
    )
    def get(self, request, *args, **kwargs):
        """Get goal details."""
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update Goal",
        description="Update a goal's details.",
        responses={
            200: GoalSerializer,
            400: "Validation error",
            404: "Goal not found",
            401: "Authentication required"
        }
    )
    def patch(self, request, *args, **kwargs):
        """Update goal."""
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete Goal",
        description="Delete a goal.",
        responses={
            204: "Goal deleted",
            404: "Goal not found",
            401: "Authentication required"
        }
    )
    def delete(self, request, *args, **kwargs):
        """Delete goal."""
        return super().delete(request, *args, **kwargs)


class GoalCategoryListView(generics.ListCreateAPIView):
    """
    Goal category list and creation endpoint.
    """
    
    queryset = GoalCategory.objects.filter(is_active=True)
    serializer_class = GoalCategorySerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="List Goal Categories",
        description="Get a list of goal categories.",
        responses={
            200: GoalCategorySerializer(many=True),
            401: "Authentication required"
        }
    )
    def get(self, request, *args, **kwargs):
        """Get list of goal categories."""
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create Goal Category",
        description="Create a new goal category.",
        responses={
            201: GoalCategorySerializer,
            400: "Validation error",
            401: "Authentication required"
        }
    )
    def post(self, request, *args, **kwargs):
        """Create a new goal category."""
        return super().post(request, *args, **kwargs)


# Manager-specific views for goal review and approval

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@extend_schema(
    summary="Get Manager Goals",
    description="Get goals for direct reports that need manager review.",
    responses={
        200: GoalListSerializer(many=True),
        401: "Authentication required"
    }
)
def get_manager_goals(request):
    """
    Get goals for direct reports that need manager review.
    """
    user = request.user
    
    # Get goals for direct reports
    queryset = Goal.objects.select_related('employee', 'cycle', 'approved_by').filter(
        employee__manager=user
    ).order_by('-created_at')
    
    # Apply filters
    status_filter = request.query_params.get('status')
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    
    search = request.query_params.get('search')
    if search:
        queryset = queryset.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search) |
            Q(employee__first_name__icontains=search) |
            Q(employee__last_name__icontains=search)
        )
    
    serializer = GoalListSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@extend_schema(
    summary="Submit Goal Review",
    description="Submit manager review for a goal (approve, request changes, etc.).",
    responses={
        200: "Review submitted successfully",
        400: "Validation error",
        401: "Authentication required",
        404: "Goal not found"
    }
)
def submit_goal_review(request, goal_id):
    """
    Submit manager review for a goal.
    """
    try:
        goal = Goal.objects.get(id=goal_id, employee__manager=request.user)
    except Goal.DoesNotExist:
        return Response(
            {'error': 'Goal not found or you are not authorized to review this goal'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    action = request.data.get('action')
    feedback = request.data.get('feedback', '')
    alignment_comments = request.data.get('alignment_comments', '')
    workload_assessment = request.data.get('workload_assessment', 3)
    workload_comments = request.data.get('workload_comments', '')
    smart_criteria = request.data.get('smart_criteria', {})
    
    if not action:
        return Response(
            {'error': 'Action is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not feedback or len(feedback.strip()) < 10:
        return Response(
            {'error': 'Feedback must be at least 10 characters'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update goal status based on action
    if action == 'approve':
        goal.status = 'approved'
        goal.approved_by = request.user
        goal.approved_at = timezone.now()
    elif action == 'request_changes':
        goal.status = 'needs_changes'
    elif action == 'suggest_modifications':
        goal.status = 'needs_changes'
    
    # Update goal with review data
    goal.notes = f"Manager Review: {feedback}"
    goal.last_updated = timezone.now()
    goal.save()
    
    # Create a goal update record for audit trail
    GoalUpdate.objects.create(
        goal=goal,
        updated_by=request.user,
        update_type='manager_review',
        description=f"Manager review: {action}",
        notes=feedback
    )
    
    return Response({
        'message': 'Review submitted successfully',
        'goal_status': goal.status
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@extend_schema(
    summary="Approve Goal",
    description="Approve a goal with optional feedback.",
    responses={
        200: "Goal approved successfully",
        400: "Validation error",
        401: "Authentication required",
        404: "Goal not found"
    }
)
def approve_goal(request, goal_id):
    """
    Approve a goal.
    """
    try:
        goal = Goal.objects.get(id=goal_id, employee__manager=request.user)
    except Goal.DoesNotExist:
        return Response(
            {'error': 'Goal not found or you are not authorized to approve this goal'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    feedback = request.data.get('feedback', 'Goal approved by manager')
    
    goal.status = 'approved'
    goal.approved_by = request.user
    goal.approved_at = timezone.now()
    goal.notes = f"Approved: {feedback}"
    goal.last_updated = timezone.now()
    goal.save()
    
    # Create audit trail
    GoalUpdate.objects.create(
        goal=goal,
        updated_by=request.user,
        update_type='approval',
        description='Goal approved by manager',
        notes=feedback
    )
    
    return Response({
        'message': 'Goal approved successfully',
        'goal_status': goal.status
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@extend_schema(
    summary="Get Goal History",
    description="Get version history and updates for a goal.",
    responses={
        200: GoalUpdateSerializer(many=True),
        401: "Authentication required",
        404: "Goal not found"
    }
)
def get_goal_history(request, goal_id):
    """
    Get version history and updates for a goal.
    """
    try:
        goal = Goal.objects.get(id=goal_id)
        # Check if user has access to this goal
        if not (goal.employee == request.user or 
                goal.employee.manager == request.user or 
                request.user.is_hr):
            return Response(
                {'error': 'You are not authorized to view this goal'},
                status=status.HTTP_403_FORBIDDEN
            )
    except Goal.DoesNotExist:
        return Response(
            {'error': 'Goal not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    updates = GoalUpdate.objects.filter(goal=goal).order_by('-created_at')
    serializer = GoalUpdateSerializer(updates, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@extend_schema(
    summary="Submit Bulk Feedback",
    description="Submit feedback for multiple goals at once.",
    responses={
        200: "Bulk feedback submitted successfully",
        400: "Validation error",
        401: "Authentication required"
    }
)
def submit_bulk_feedback(request):
    """
    Submit feedback for multiple goals at once.
    """
    goal_ids = request.data.get('goal_ids', [])
    action = request.data.get('action')
    general_feedback = request.data.get('general_feedback', '')
    individual_feedback = request.data.get('individual_feedback', {})
    additional_comments = request.data.get('additional_comments', '')
    smart_assessment = request.data.get('smart_assessment', {})
    
    if not goal_ids:
        return Response(
            {'error': 'Goal IDs are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not action:
        return Response(
            {'error': 'Action is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not general_feedback or len(general_feedback.strip()) < 10:
        return Response(
            {'error': 'General feedback must be at least 10 characters'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get goals that the manager can review
    goals = Goal.objects.filter(
        id__in=goal_ids,
        employee__manager=request.user
    )
    
    if not goals.exists():
        return Response(
            {'error': 'No goals found or you are not authorized to review these goals'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    updated_goals = []
    
    for goal in goals:
        # Get individual feedback for this goal
        individual_fb = individual_feedback.get(str(goal.id), general_feedback)
        
        # Update goal status
        if action == 'approve':
            goal.status = 'approved'
            goal.approved_by = request.user
            goal.approved_at = timezone.now()
        elif action in ['request_changes', 'suggest_modifications']:
            goal.status = 'needs_changes'
        
        goal.notes = f"Bulk Review ({action}): {individual_fb}"
        goal.last_updated = timezone.now()
        goal.save()
        
        # Create audit trail
        GoalUpdate.objects.create(
            goal=goal,
            updated_by=request.user,
            update_type='bulk_review',
            description=f'Bulk review: {action}',
            notes=individual_fb
        )
        
        updated_goals.append(goal.id)
    
    return Response({
        'message': f'Bulk feedback submitted for {len(updated_goals)} goal(s)',
        'updated_goals': updated_goals
    })