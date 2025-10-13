"""
Manager review views for goals.
Implements BR-017, BR-018, BR-019, BR-020, BR-021.
"""

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db.models import Q, Count
from django.core.exceptions import ValidationError as DjangoValidationError

from .models import Goal, GoalFeedback, GoalVersion
from .serializers import GoalSerializer, GoalFeedbackSerializer, GoalVersionSerializer
from apps.accounts.models import User


class ManagerTeamGoalsView(generics.ListAPIView):
    """
    Manager dashboard for team goal review.
    Shows all direct report goals with filtering and sorting.
    BR-020: Managers can only see goals for direct reports.
    """
    
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get goals for manager's direct reports."""
        user = self.request.user
        
        # Only managers and HR can access
        if user.role not in ['manager', 'hr', 'admin']:
            return Goal.objects.none()
        
        # Get manager's direct reports
        if user.role == 'manager':
            direct_reports = User.objects.filter(manager=user)
            queryset = Goal.objects.filter(employee__in=direct_reports)
        else:
            # HR can see all goals
            queryset = Goal.objects.all()
        
        queryset = queryset.select_related('employee', 'cycle', 'approved_by').prefetch_related('feedback')
        
        # Filter by status (pending goals first)
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        else:
            # Default: show pending goals
            queryset = queryset.filter(status='submitted')
        
        # Filter by employee
        employee_id = self.request.query_params.get('employee_id')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        # Sort by oldest first (priority queue)
        sort_by = self.request.query_params.get('sort', 'created_at')
        if sort_by == 'priority':
            queryset = queryset.order_by('-priority', 'created_at')
        elif sort_by == 'employee':
            queryset = queryset.order_by('employee__last_name', 'employee__first_name')
        else:
            queryset = queryset.order_by('created_at')  # Oldest first
        
        return queryset
    
    @extend_schema(
        summary="Manager Team Goals Dashboard",
        description="List all direct report goals for manager review (BR-020)",
        parameters=[
            OpenApiParameter('status', OpenApiTypes.STR, description='Filter by goal status (default: submitted)'),
            OpenApiParameter('employee_id', OpenApiTypes.INT, description='Filter by employee ID'),
            OpenApiParameter('sort', OpenApiTypes.STR, description='Sort by: created_at, priority, employee'),
        ],
        responses={200: GoalSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        """Get team goals for review."""
        return super().get(request, *args, **kwargs)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@extend_schema(
    summary="Approve Employee Goal",
    description="Manager approves employee goal (BR-017: Manager approval required)",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'comments': {'type': 'string', 'description': 'Optional positive feedback'},
                'smart_specific': {'type': 'boolean'},
                'smart_measurable': {'type': 'boolean'},
                'smart_achievable': {'type': 'boolean'},
                'smart_relevant': {'type': 'boolean'},
                'smart_time_bound': {'type': 'boolean'},
                'alignment_score': {'type': 'integer', 'minimum': 1, 'maximum': 5},
                'challenge_level': {'type': 'string', 'enum': ['too_easy', 'appropriate', 'too_ambitious']},
            }
        }
    },
    responses={
        200: GoalSerializer,
        400: "Validation error",
        403: "Not authorized to approve this goal",
        404: "Goal not found"
    }
)
def approve_goal(request, goal_id):
    """
    Approve an employee goal.
    BR-017: Manager approval required before goals become active.
    BR-020: Managers can only approve goals for direct reports.
    """
    try:
        goal = Goal.objects.select_related('employee').get(pk=goal_id)
    except Goal.DoesNotExist:
        return Response(
            {'error': 'Goal not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # BR-020: Verify manager-employee relationship
    if request.user.role == 'manager':
        if goal.employee.manager != request.user:
            return Response(
                {'error': 'You can only approve goals for your direct reports'},
                status=status.HTTP_403_FORBIDDEN
            )
    elif request.user.role not in ['hr', 'admin']:
        return Response(
            {'error': 'Only managers and HR can approve goals'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check if goal is in submitted status
    if goal.status != 'submitted':
        return Response(
            {'error': f'Goal must be in "submitted" status to be approved. Current status: {goal.status}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Approve the goal
    try:
        goal.approve(request.user)
    except DjangoValidationError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create approval feedback
    feedback_data = request.data
    GoalFeedback.objects.create(
        goal=goal,
        manager=request.user,
        feedback_type='approval',
        comments=feedback_data.get('comments', 'Goal approved'),
        smart_specific=feedback_data.get('smart_specific', True),
        smart_measurable=feedback_data.get('smart_measurable', True),
        smart_achievable=feedback_data.get('smart_achievable', True),
        smart_relevant=feedback_data.get('smart_relevant', True),
        smart_time_bound=feedback_data.get('smart_time_bound', True),
        alignment_score=feedback_data.get('alignment_score'),
        challenge_level=feedback_data.get('challenge_level'),
    )
    
    serializer = GoalSerializer(goal, context={'request': request})
    return Response({
        'message': 'Goal approved successfully',
        'goal': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@extend_schema(
    summary="Request Changes to Goal",
    description="Manager requests changes to employee goal (BR-018: Feedback mandatory)",
    request={
        'application/json': {
            'type': 'object',
            'required': ['comments'],
            'properties': {
                'comments': {'type': 'string', 'minLength': 10, 'description': 'Required detailed feedback'},
                'feedback_type': {'type': 'string', 'enum': ['request_changes', 'rejection'], 'default': 'request_changes'},
                'smart_specific': {'type': 'boolean'},
                'smart_measurable': {'type': 'boolean'},
                'smart_achievable': {'type': 'boolean'},
                'smart_relevant': {'type': 'boolean'},
                'smart_time_bound': {'type': 'boolean'},
                'suggested_modifications': {'type': 'string'},
                'challenge_level': {'type': 'string', 'enum': ['too_easy', 'appropriate', 'too_ambitious']},
            }
        }
    },
    responses={
        200: GoalSerializer,
        400: "Validation error or missing feedback",
        403: "Not authorized",
        404: "Goal not found"
    }
)
def request_goal_changes(request, goal_id):
    """
    Request changes or reject employee goal.
    BR-018: Manager feedback is mandatory for goal rejections.
    BR-020: Managers can only review goals for direct reports.
    """
    try:
        goal = Goal.objects.select_related('employee').get(pk=goal_id)
    except Goal.DoesNotExist:
        return Response(
            {'error': 'Goal not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # BR-020: Verify manager-employee relationship
    if request.user.role == 'manager':
        if goal.employee.manager != request.user:
            return Response(
                {'error': 'You can only review goals for your direct reports'},
                status=status.HTTP_403_FORBIDDEN
            )
    elif request.user.role not in ['hr', 'admin']:
        return Response(
            {'error': 'Only managers and HR can review goals'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # BR-018: Validate feedback comments
    comments = request.data.get('comments', '').strip()
    if not comments or len(comments) < 10:
        return Response(
            {'error': 'Detailed feedback is required (minimum 10 characters). '
                     'Provide specific guidance for the employee to improve their goal.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    feedback_type = request.data.get('feedback_type', 'request_changes')
    
    # Reject or request changes
    try:
        if feedback_type == 'rejection':
            goal.reject(request.user, comments)
        else:
            goal.status = 'rejected'  # Use same status for changes needed
            goal.save()
    except DjangoValidationError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create feedback record
    GoalFeedback.objects.create(
        goal=goal,
        manager=request.user,
        feedback_type=feedback_type,
        comments=comments,
        smart_specific=request.data.get('smart_specific', True),
        smart_measurable=request.data.get('smart_measurable', True),
        smart_achievable=request.data.get('smart_achievable', True),
        smart_relevant=request.data.get('smart_relevant', True),
        smart_time_bound=request.data.get('smart_time_bound', True),
        suggested_modifications=request.data.get('suggested_modifications', ''),
        challenge_level=request.data.get('challenge_level'),
    )
    
    serializer = GoalSerializer(goal, context={'request': request})
    action_text = 'rejected' if feedback_type == 'rejection' else 'marked for revision'
    return Response({
        'message': f'Goal {action_text}. Employee has been notified with your feedback.',
        'goal': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@extend_schema(
    summary="Get Goal Version History",
    description="View complete goal version history (BR-019: Version history preserved)",
    responses={200: GoalVersionSerializer(many=True)}
)
def goal_version_history(request, goal_id):
    """
    Get version history for a goal.
    BR-019: Goal versions preserved for audit trail.
    """
    try:
        goal = Goal.objects.get(pk=goal_id)
    except Goal.DoesNotExist:
        return Response(
            {'error': 'Goal not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check permissions
    if request.user == goal.employee or request.user == goal.employee.manager or request.user.role in ['hr', 'admin']:
        versions = goal.versions.all().order_by('-version_number')
        serializer = GoalVersionSerializer(versions, many=True)
        return Response(serializer.data)
    else:
        return Response(
            {'error': 'You do not have permission to view this goal\'s history'},
            status=status.HTTP_403_FORBIDDEN
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@extend_schema(
    summary="Get Goal Feedback History",
    description="View all feedback for a goal",
    responses={200: GoalFeedbackSerializer(many=True)}
)
def goal_feedback_history(request, goal_id):
    """Get all feedback for a goal."""
    try:
        goal = Goal.objects.get(pk=goal_id)
    except Goal.DoesNotExist:
        return Response(
            {'error': 'Goal not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check permissions
    if request.user == goal.employee or request.user == goal.employee.manager or request.user.role in ['hr', 'admin']:
        feedback = goal.feedback.all().order_by('-created_at')
        serializer = GoalFeedbackSerializer(feedback, many=True)
        return Response(serializer.data)
    else:
        return Response(
            {'error': 'You do not have permission to view this goal\'s feedback'},
            status=status.HTTP_403_FORBIDDEN
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@extend_schema(
    summary="Add Manager Feedback/Suggestion",
    description="Manager adds feedback or suggestions without changing goal status",
    request=GoalFeedbackSerializer,
    responses={201: GoalFeedbackSerializer}
)
def add_goal_feedback(request, goal_id):
    """
    Add feedback or suggestions to a goal without changing status.
    Useful for alignment comments or suggestions.
    """
    try:
        goal = Goal.objects.get(pk=goal_id)
    except Goal.DoesNotExist:
        return Response(
            {'error': 'Goal not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # BR-020: Verify manager-employee relationship
    if request.user.role == 'manager':
        if goal.employee.manager != request.user:
            return Response(
                {'error': 'You can only provide feedback for your direct reports'},
                status=status.HTTP_403_FORBIDDEN
            )
    elif request.user.role not in ['hr', 'admin']:
        return Response(
            {'error': 'Only managers and HR can provide feedback'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Create feedback
    data = request.data.copy()
    data['goal'] = goal.id
    
    serializer = GoalFeedbackSerializer(data=data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@extend_schema(
    summary="Manager Goal Review Dashboard Stats",
    description="Get statistics for manager goal review dashboard",
    responses={
        200: {
            'type': 'object',
            'properties': {
                'pending_count': {'type': 'integer'},
                'approved_count': {'type': 'integer'},
                'rejected_count': {'type': 'integer'},
                'total_direct_reports': {'type': 'integer'},
                'direct_reports_with_goals': {'type': 'integer'},
                'oldest_pending_goal': {'type': 'object'},
            }
        }
    }
)
def manager_goal_stats(request):
    """
    Get goal review statistics for manager dashboard.
    """
    user = request.user
    
    if user.role not in ['manager', 'hr', 'admin']:
        return Response(
            {'error': 'Only managers and HR can access these statistics'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get manager's direct reports
    if user.role == 'manager':
        direct_reports = User.objects.filter(manager=user)
        goals = Goal.objects.filter(employee__in=direct_reports)
    else:
        # HR sees all
        direct_reports = User.objects.filter(is_active=True)
        goals = Goal.objects.all()
    
    # Calculate statistics
    stats = {
        'pending_count': goals.filter(status='submitted').count(),
        'approved_count': goals.filter(status='approved').count(),
        'rejected_count': goals.filter(status='rejected').count(),
        'total_direct_reports': direct_reports.count(),
        'direct_reports_with_goals': goals.values('employee').distinct().count(),
    }
    
    # Get oldest pending goal
    oldest_pending = goals.filter(status='submitted').order_by('created_at').first()
    if oldest_pending:
        stats['oldest_pending_goal'] = {
            'id': oldest_pending.id,
            'employee': oldest_pending.employee.full_name,
            'title': oldest_pending.title,
            'submitted_at': oldest_pending.created_at
        }
    else:
        stats['oldest_pending_goal'] = None
    
    return Response(stats)

