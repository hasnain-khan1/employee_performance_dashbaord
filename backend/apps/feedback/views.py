"""
Views for the feedback app.

This module contains API views for peer feedback system including
request management, response collection, and content policy enforcement.
"""

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import (
    FeedbackRequest, FeedbackResponse, FeedbackTemplate,
    PeerReviewer, ContentPolicyRule, ManagerFeedback
)
from .serializers import (
    FeedbackRequestSerializer, FeedbackRequestListSerializer,
    FeedbackResponseSerializer, FeedbackTemplateSerializer,
    PeerReviewerSerializer, ContentPolicyRuleSerializer,
    FeedbackResponseListSerializer, ManagerFeedbackSerializer,
    ManagerFeedbackListSerializer, ManagerFeedbackCreateSerializer,
    ManagerFeedbackAcknowledgeSerializer
)

User = get_user_model()


class FeedbackRequestListView(generics.ListCreateAPIView):
    """
    Feedback request list and creation endpoint.
    
    Provides list of peer feedback requests with filtering,
    and allows creation of new feedback requests.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method == 'GET':
            return FeedbackRequestListSerializer
        return FeedbackRequestSerializer
    
    def get_queryset(self):
        """Get filtered queryset of feedback requests."""
        user = self.request.user
        queryset = FeedbackRequest.objects.select_related('requester', 'cycle')
        
        # Filter based on user role
        view_type = self.request.query_params.get('view')
        if view_type == 'sent':
            queryset = queryset.filter(requester=user)
        elif view_type == 'received':
            # Show requests where user is a peer reviewer
            queryset = queryset.filter(peer_reviewers__reviewer=user)
        else:
            # Default: show all requests where user is involved
            queryset = queryset.filter(
                Q(requester=user) | Q(peer_reviewers__reviewer=user)
            ).distinct()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by cycle
        cycle = self.request.query_params.get('cycle')
        if cycle:
            queryset = queryset.filter(cycle_id=cycle)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set requester to current user when creating."""
        serializer.save(requester=self.request.user)
    
    @extend_schema(
        summary="List Feedback Requests",
        description="Get a list of peer feedback requests with optional filtering.",
        parameters=[
            OpenApiParameter(
                name='view',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by view type: "sent" or "received"'
            ),
            OpenApiParameter(
                name='status',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by status'
            ),
            OpenApiParameter(
                name='cycle',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter by cycle ID'
            ),
        ],
        responses={
            200: FeedbackRequestListSerializer(many=True),
            401: "Authentication required"
        }
    )
    def get(self, request, *args, **kwargs):
        """Get list of feedback requests."""
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create Feedback Request",
        description="Create a new peer feedback request.",
        responses={
            201: FeedbackRequestSerializer,
            400: "Validation error",
            401: "Authentication required"
        }
    )
    def post(self, request, *args, **kwargs):
        """Create a new feedback request."""
        return super().post(request, *args, **kwargs)


class FeedbackRequestDetailView(generics.RetrieveUpdateAPIView):
    """
    Feedback request detail endpoint.
    
    Provides detailed information about a specific feedback request
    and allows updates to status and submission.
    """
    
    serializer_class = FeedbackRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'
    
    def get_queryset(self):
        """Get queryset filtered by user involvement."""
        user = self.request.user
        return FeedbackRequest.objects.filter(
            Q(requester=user) | Q(peer_reviewers__reviewer=user)
        ).distinct()
    
    @extend_schema(
        summary="Get Feedback Request Details",
        description="Retrieve detailed information about a specific feedback request.",
        responses={
            200: FeedbackRequestSerializer,
            404: "Feedback request not found",
            401: "Authentication required"
        }
    )
    def get(self, request, *args, **kwargs):
        """Get feedback request details."""
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update Feedback Request",
        description="Update a feedback request status or details.",
        responses={
            200: FeedbackRequestSerializer,
            400: "Validation error",
            404: "Feedback request not found",
            401: "Authentication required"
        }
    )
    def patch(self, request, *args, **kwargs):
        """Update feedback request."""
        return super().patch(request, *args, **kwargs)


class FeedbackResponseCreateView(generics.CreateAPIView):
    """
    Feedback response creation endpoint.
    
    Allows peer reviewers to submit feedback responses.
    """
    
    serializer_class = FeedbackResponseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Submit Feedback Response",
        description="Submit a feedback response to a peer review request.",
        responses={
            201: FeedbackResponseSerializer,
            400: "Validation error",
            401: "Authentication required"
        }
    )
    def post(self, request, *args, **kwargs):
        """Submit feedback response."""
        return super().post(request, *args, **kwargs)


class FeedbackTemplateListView(generics.ListCreateAPIView):
    """
    Feedback template list and creation endpoint.
    
    Provides list of feedback templates and allows creation
    of new templates (HR only).
    """
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FeedbackTemplateSerializer
    
    def get_queryset(self):
        """Get queryset of active feedback templates."""
        queryset = FeedbackTemplate.objects.all()
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('name')
    
    @extend_schema(
        summary="List Feedback Templates",
        description="Get a list of feedback templates.",
        parameters=[
            OpenApiParameter(
                name='is_active',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter by active status'
            ),
        ],
        responses={
            200: FeedbackTemplateSerializer(many=True),
            401: "Authentication required"
        }
    )
    def get(self, request, *args, **kwargs):
        """Get list of feedback templates."""
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create Feedback Template",
        description="Create a new feedback template (HR only).",
        responses={
            201: FeedbackTemplateSerializer,
            400: "Validation error",
            401: "Authentication required",
            403: "Permission denied"
        }
    )
    def post(self, request, *args, **kwargs):
        """Create a new feedback template."""
        # Check if user is HR or admin
        if not request.user.is_hr:
            return Response(
                {'error': 'Only HR can create feedback templates'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().post(request, *args, **kwargs)


# Peer Selection and Management Views

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="Get Available Peers",
    description="Get list of colleagues available for peer feedback selection.",
    parameters=[
        OpenApiParameter(
            name='department',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Filter by department'
        ),
        OpenApiParameter(
            name='search',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Search by name or email'
        ),
    ],
    responses={
        200: "List of available peers",
        401: "Authentication required"
    }
)
def get_available_peers(request):
    """
    Get list of colleagues available for peer feedback selection.
    """
    user = request.user
    
    # Get all users except the current user
    queryset = User.objects.exclude(id=user.id).filter(is_active=True)
    
    # Filter by department
    department = request.query_params.get('department')
    if department:
        queryset = queryset.filter(department=department)
    
    # Search by name or email
    search = request.query_params.get('search')
    if search:
        queryset = queryset.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    # Serialize and return
    from .serializers import UserListSerializer
    serializer = UserListSerializer(queryset[:50], many=True)  # Limit to 50 results
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="Create Peer Feedback Request",
    description="Create a new peer feedback request with selected reviewers.",
    responses={
        201: FeedbackRequestSerializer,
        400: "Validation error",
        401: "Authentication required"
    }
)
def create_peer_feedback_request(request):
    """
    Create a new peer feedback request with selected reviewers.
    """
    # Validate required fields
    title = request.data.get('title')
    deadline = request.data.get('deadline')
    peer_reviewer_ids = request.data.get('peer_reviewer_ids', [])
    
    if not title:
        return Response(
            {'error': 'Title is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not deadline:
        return Response(
            {'error': 'Deadline is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not peer_reviewer_ids:
        return Response(
            {'error': 'At least one peer reviewer is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate peer count (1-5)
    if len(peer_reviewer_ids) < 1 or len(peer_reviewer_ids) > 5:
        return Response(
            {'error': 'Must select between 1 and 5 peer reviewers'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get or create active cycle
    from apps.cycles.models import ReviewCycle
    cycle = ReviewCycle.objects.filter(is_active=True).first()
    if not cycle:
        return Response(
            {'error': 'No active review cycle found'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create feedback request
    feedback_request = FeedbackRequest.objects.create(
        requester=request.user,
        cycle=cycle,
        title=title,
        description=request.data.get('description', ''),
        deadline=deadline,
        allow_anonymous=request.data.get('allow_anonymous', True),
        min_peers=1,
        max_peers=5
    )
    
    # Create peer reviewers
    for reviewer_id in peer_reviewer_ids:
        try:
            reviewer = User.objects.get(id=reviewer_id)
            PeerReviewer.objects.create(
                feedback_request=feedback_request,
                reviewer=reviewer,
                relationship_context=request.data.get('relationship_context', ''),
                personal_message=request.data.get('personal_message', '')
            )
        except User.DoesNotExist:
            continue
    
    # Update status to sent
    feedback_request.status = 'sent'
    feedback_request.save()
    
    serializer = FeedbackRequestSerializer(feedback_request)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# Content Policy Enforcement

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="Validate Content Policy",
    description="Validate feedback content against policy rules.",
    responses={
        200: "Content validation results",
        401: "Authentication required"
    }
)
def validate_content_policy(request):
    """
    Validate feedback content against content policy rules.
    """
    content = request.data.get('content', '')
    violations = []
    
    # Get active content policy rules
    rules = ContentPolicyRule.objects.filter(is_active=True)
    
    for rule in rules:
        rule_violations = []
        
        # Check keywords
        for keyword in rule.keywords:
            if keyword.lower() in content.lower():
                rule_violations.append(f"Contains flagged keyword: {keyword}")
        
        # Check patterns (basic implementation)
        for pattern in rule.patterns:
            if pattern in content:
                rule_violations.append(f"Matches flagged pattern: {pattern}")
        
        # Check length requirements
        if rule.min_length and len(content) < rule.min_length:
            rule_violations.append(f"Content too short (minimum {rule.min_length} characters)")
        
        if rule.max_length and len(content) > rule.max_length:
            rule_violations.append(f"Content too long (maximum {rule.max_length} characters)")
        
        if rule_violations:
            violations.append({
                'rule_name': rule.name,
                'rule_type': rule.rule_type,
                'severity': rule.severity,
                'violations': rule_violations,
                'warning_message': rule.warning_message,
                'auto_block': rule.auto_block
            })
    
    # Determine if content should be blocked
    critical_violations = [v for v in violations if v['severity'] == 'critical']
    auto_block_violations = [v for v in violations if v['auto_block']]
    
    should_block = len(critical_violations) > 0 or len(auto_block_violations) > 0
    
    return Response({
        'violations': violations,
        'should_block': should_block,
        'is_valid': len(violations) == 0
    })


# Automated Reminder System

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="Send Reminder",
    description="Send reminder to peer reviewers (HR/Manager only).",
    responses={
        200: "Reminder sent successfully",
        401: "Authentication required",
        403: "Permission denied"
    }
)
def send_reminder(request, peer_reviewer_id):
    """
    Send reminder to a specific peer reviewer.
    """
    # Check if user is HR or manager
    if not (request.user.is_hr or request.user.is_manager):
        return Response(
            {'error': 'Only HR or managers can send reminders'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        peer_reviewer = PeerReviewer.objects.get(id=peer_reviewer_id)
    except PeerReviewer.DoesNotExist:
        return Response(
            {'error': 'Peer reviewer not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Update reminder tracking
    peer_reviewer.reminder_sent_count += 1
    peer_reviewer.last_reminder_sent = timezone.now()
    peer_reviewer.save()
    
    # TODO: Send actual email notification
    # This would integrate with your email service
    
    return Response({
        'message': 'Reminder sent successfully',
        'reminder_count': peer_reviewer.reminder_sent_count
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="Get Feedback Statistics",
    description="Get statistics for feedback requests and responses.",
    responses={
        200: "Feedback statistics",
        401: "Authentication required"
    }
)
def get_feedback_statistics(request):
    """
    Get statistics for feedback requests and responses.
    """
    user = request.user
    
    # Get user's feedback requests
    sent_requests = FeedbackRequest.objects.filter(requester=user)
    received_requests = FeedbackRequest.objects.filter(peer_reviewers__reviewer=user)
    
    # Calculate statistics
    stats = {
        'sent_requests': {
            'total': sent_requests.count(),
            'completed': sent_requests.filter(status='completed').count(),
            'in_progress': sent_requests.filter(status='in_progress').count(),
            'expired': sent_requests.filter(status='expired').count()
        },
        'received_requests': {
            'total': received_requests.count(),
            'completed': received_requests.filter(peer_reviewers__status='completed').count(),
            'pending': received_requests.filter(peer_reviewers__status='pending').count(),
            'overdue': received_requests.filter(
                peer_reviewers__status__in=['pending', 'in_progress'],
                deadline__lt=timezone.now()
            ).count()
        }
    }
    
    return Response(stats)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="Cancel Feedback Request",
    description="Cancel a feedback request (requester only).",
    responses={
        200: "Request cancelled successfully",
        401: "Authentication required",
        404: "Request not found",
        403: "Permission denied"
    }
)
def cancel_feedback_request(request, pk):
    """
    Cancel a feedback request.
    """
    try:
        feedback_request = FeedbackRequest.objects.get(pk=pk, requester=request.user)
    except FeedbackRequest.DoesNotExist:
        return Response(
            {'error': 'Feedback request not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Only allow cancellation if not completed
    if feedback_request.status == 'completed':
        return Response(
            {'error': 'Cannot cancel completed feedback request'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    feedback_request.status = 'cancelled'
    feedback_request.save()
    
    return Response({
        'message': 'Feedback request cancelled successfully',
        'status': feedback_request.status
    })


# Manager Feedback Views
class ManagerFeedbackListView(generics.ListCreateAPIView):
    """List and create manager feedback."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ManagerFeedbackListSerializer
        return ManagerFeedbackCreateSerializer
    
    def get_queryset(self):
        user = self.request.user
        view_type = self.request.query_params.get('view', 'given')
        
        if view_type == 'given':
            # Manager feedback given by the user
            queryset = ManagerFeedback.objects.filter(manager=user)
        elif view_type == 'received':
            # Manager feedback received by the user
            queryset = ManagerFeedback.objects.filter(employee=user)
        else:
            # Default: all feedback where user is involved
            queryset = ManagerFeedback.objects.filter(
                Q(manager=user) | Q(employee=user)
            ).distinct()
        
        # Apply filters
        employee_id = self.request.query_params.get('employee_id')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        feedback_type = self.request.query_params.get('feedback_type')
        if feedback_type:
            queryset = queryset.filter(feedback_type=feedback_type)
        
        is_acknowledged = self.request.query_params.get('is_acknowledged')
        if is_acknowledged is not None:
            queryset = queryset.filter(is_acknowledged=is_acknowledged.lower() == 'true')
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(manager=self.request.user)


class ManagerFeedbackDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete manager feedback."""
    
    serializer_class = ManagerFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return ManagerFeedback.objects.filter(
            Q(manager=user) | Q(employee=user)
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="Acknowledge Manager Feedback",
    description="Allow employee to acknowledge and respond to manager feedback.",
    responses={
        200: ManagerFeedbackSerializer,
        400: "Validation error",
        401: "Authentication required",
        404: "Feedback not found"
    }
)
def acknowledge_manager_feedback(request, pk):
    """Allow employee to acknowledge manager feedback."""
    try:
        feedback = get_object_or_404(
            ManagerFeedback,
            pk=pk,
            employee=request.user
        )
        
        serializer = ManagerFeedbackAcknowledgeSerializer(
            feedback,
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )