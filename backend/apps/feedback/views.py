"""
Views for the feedback app.

This module contains API views for feedback request and response management.
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db.models import Q
from django.utils import timezone

from .models import FeedbackRequest, FeedbackResponse, FeedbackTemplate, ManagerFeedback
from .serializers import (
    FeedbackRequestSerializer, FeedbackRequestListSerializer,
    FeedbackResponseSerializer, FeedbackTemplateSerializer,
    FeedbackTemplateListSerializer, ManagerFeedbackSerializer,
    ManagerFeedbackListSerializer
)


class FeedbackRequestListView(generics.ListCreateAPIView):
    """
    Feedback request list and creation endpoint.
    
    Provides list of feedback requests with filtering,
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
        queryset = FeedbackRequest.objects.select_related(
            'requester', 'recipient', 'cycle'
        )
        
        # Filter based on user role
        view_type = self.request.query_params.get('view')
        if view_type == 'sent':
            queryset = queryset.filter(requester=user)
        elif view_type == 'received':
            queryset = queryset.filter(recipient=user)
        else:
            # Default: show all requests where user is involved
            queryset = queryset.filter(
                Q(requester=user) | Q(recipient=user)
            )
        
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
        description="Get a list of feedback requests with optional filtering.",
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
        description="Create a new feedback request.",
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
            Q(requester=user) | Q(recipient=user)
        )
    
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
    
    Allows recipients to submit feedback responses.
    """
    
    serializer_class = FeedbackResponseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Submit Feedback Response",
        description="Submit a feedback response to a request.",
        responses={
            201: FeedbackResponseSerializer,
            400: "Validation error",
            401: "Authentication required"
        }
    )
    def post(self, request, *args, **kwargs):
        """Submit feedback response."""
        response = super().post(request, *args, **kwargs)
        
        # Update the request status to completed
        if response.status_code == status.HTTP_201_CREATED:
            request_id = request.data.get('request_id')
            if request_id:
                feedback_request = FeedbackRequest.objects.get(id=request_id)
                feedback_request.status = 'completed'
                feedback_request.submitted_at = timezone.now()
                feedback_request.save()
        
        return response


class FeedbackTemplateListView(generics.ListCreateAPIView):
    """
    Feedback template list and creation endpoint.
    
    Provides list of feedback templates and allows creation
    of new templates (HR only).
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method == 'GET':
            return FeedbackTemplateListSerializer
        return FeedbackTemplateSerializer
    
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
            200: FeedbackTemplateListSerializer(many=True),
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


class FeedbackTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Feedback template detail endpoint.
    
    Provides detailed information about a specific template
    and allows updates (HR only).
    """
    
    serializer_class = FeedbackTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = FeedbackTemplate.objects.all()
    lookup_field = 'pk'
    
    @extend_schema(
        summary="Get Feedback Template Details",
        description="Retrieve detailed information about a specific feedback template.",
        responses={
            200: FeedbackTemplateSerializer,
            404: "Template not found",
            401: "Authentication required"
        }
    )
    def get(self, request, *args, **kwargs):
        """Get feedback template details."""
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update Feedback Template",
        description="Update a feedback template (HR only).",
        responses={
            200: FeedbackTemplateSerializer,
            400: "Validation error",
            404: "Template not found",
            401: "Authentication required",
            403: "Permission denied"
        }
    )
    def patch(self, request, *args, **kwargs):
        """Update feedback template."""
        if not request.user.is_hr:
            return Response(
                {'error': 'Only HR can update feedback templates'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete Feedback Template",
        description="Delete a feedback template (HR only).",
        responses={
            204: "Template deleted",
            404: "Template not found",
            401: "Authentication required",
            403: "Permission denied"
        }
    )
    def delete(self, request, *args, **kwargs):
        """Delete feedback template."""
        if not request.user.is_hr:
            return Response(
                {'error': 'Only HR can delete feedback templates'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().delete(request, *args, **kwargs)


class ManagerFeedbackListView(generics.ListCreateAPIView):
    """
    Manager feedback list and creation endpoint.
    
    Allows managers to provide feedback to their direct reports
    and employees to view feedback received from their managers.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method == 'GET':
            return ManagerFeedbackListSerializer
        return ManagerFeedbackSerializer
    
    def get_queryset(self):
        """Get filtered queryset of manager feedback."""
        user = self.request.user
        queryset = ManagerFeedback.objects.select_related(
            'manager', 'employee', 'cycle'
        )
        
        # Filter based on user role
        view_type = self.request.query_params.get('view')
        if view_type == 'given':
            # Manager view: feedback they've given
            queryset = queryset.filter(manager=user)
        elif view_type == 'received':
            # Employee view: feedback they've received
            queryset = queryset.filter(employee=user)
        else:
            # Default: show feedback where user is involved
            queryset = queryset.filter(
                Q(manager=user) | Q(employee=user)
            )
        
        # Filter by employee (for managers viewing specific employee)
        employee_id = self.request.query_params.get('employee_id')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        # Filter by feedback type
        feedback_type = self.request.query_params.get('feedback_type')
        if feedback_type:
            queryset = queryset.filter(feedback_type=feedback_type)
        
        # Filter by acknowledgment status
        is_acknowledged = self.request.query_params.get('is_acknowledged')
        if is_acknowledged is not None:
            queryset = queryset.filter(is_acknowledged=is_acknowledged.lower() == 'true')
        
        # Filter by cycle
        cycle = self.request.query_params.get('cycle')
        if cycle:
            queryset = queryset.filter(cycle_id=cycle)
        
        return queryset.order_by('-created_at')
    
    @extend_schema(
        summary="List Manager Feedback",
        description="Get a list of manager feedback with optional filtering.",
        parameters=[
            OpenApiParameter(
                name='view',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by view type: "given" or "received"'
            ),
            OpenApiParameter(
                name='employee_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter by employee ID'
            ),
            OpenApiParameter(
                name='feedback_type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by feedback type'
            ),
            OpenApiParameter(
                name='is_acknowledged',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter by acknowledgment status'
            ),
            OpenApiParameter(
                name='cycle',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter by cycle ID'
            ),
        ],
        responses={
            200: ManagerFeedbackListSerializer(many=True),
            401: "Authentication required"
        }
    )
    def get(self, request, *args, **kwargs):
        """Get list of manager feedback."""
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create Manager Feedback",
        description="Create new feedback for a direct report (Managers only).",
        responses={
            201: ManagerFeedbackSerializer,
            400: "Validation error",
            401: "Authentication required"
        }
    )
    def post(self, request, *args, **kwargs):
        """Create new manager feedback."""
        return super().post(request, *args, **kwargs)


class ManagerFeedbackDetailView(generics.RetrieveUpdateAPIView):
    """
    Manager feedback detail endpoint.
    
    Provides detailed information about a specific feedback
    and allows employees to acknowledge and respond.
    """
    
    serializer_class = ManagerFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'
    
    def get_queryset(self):
        """Get queryset filtered by user involvement."""
        user = self.request.user
        return ManagerFeedback.objects.filter(
            Q(manager=user) | Q(employee=user)
        )
    
    @extend_schema(
        summary="Get Manager Feedback Details",
        description="Retrieve detailed information about a specific feedback.",
        responses={
            200: ManagerFeedbackSerializer,
            404: "Feedback not found",
            401: "Authentication required"
        }
    )
    def get(self, request, *args, **kwargs):
        """Get feedback details."""
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update Manager Feedback",
        description="Update feedback (manager) or acknowledge/respond (employee).",
        responses={
            200: ManagerFeedbackSerializer,
            400: "Validation error",
            404: "Feedback not found",
            401: "Authentication required"
        }
    )
    def patch(self, request, *args, **kwargs):
        """Update feedback."""
        return super().patch(request, *args, **kwargs)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def acknowledge_feedback(request, pk):
    """
    Employee acknowledges receiving feedback.
    
    Allows employees to mark feedback as acknowledged and
    optionally provide a response.
    """
    try:
        feedback = ManagerFeedback.objects.get(
            pk=pk,
            employee=request.user
        )
    except ManagerFeedback.DoesNotExist:
        return Response(
            {'error': 'Feedback not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    employee_response = request.data.get('employee_response', '')
    feedback.acknowledge(response=employee_response)
    
    serializer = ManagerFeedbackSerializer(feedback)
    return Response(serializer.data)

