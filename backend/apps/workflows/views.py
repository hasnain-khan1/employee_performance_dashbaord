"""
Views for the workflows app.
"""

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from drf_spectacular.utils import extend_schema

from .models import WorkflowStep, WorkflowNotification, AuditLog
from .serializers import (
    WorkflowStepSerializer,
    WorkflowNotificationSerializer,
    AuditLogSerializer
)


class WorkflowStepListView(generics.ListCreateAPIView):
    """
    List and create workflow steps.
    """
    serializer_class = WorkflowStepSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get filtered queryset of workflow steps."""
        queryset = WorkflowStep.objects.all()
        
        # Filter by user
        user_id = self.request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by cycle
        cycle_id = self.request.query_params.get('cycle')
        if cycle_id:
            queryset = queryset.filter(cycle_id=cycle_id)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by role
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        # If no specific user requested, show current user's workflow
        if not user_id and not self.request.user.role in ['hr', 'admin']:
            queryset = queryset.filter(user=self.request.user)
        
        return queryset.select_related('user', 'cycle')


class WorkflowStepDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a workflow step.
    """
    serializer_class = WorkflowStepSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get queryset of workflow steps."""
        return WorkflowStep.objects.all()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="Update Workflow Step Status",
    description="Update the status of a workflow step.",
    request=WorkflowStepSerializer,
    responses={200: WorkflowStepSerializer}
)
def update_workflow_status(request, pk):
    """
    Update the status of a workflow step.
    """
    try:
        workflow_step = WorkflowStep.objects.get(pk=pk)
        
        # Check permissions
        if request.user.role not in ['hr', 'admin']:
            if workflow_step.user != request.user:
                return Response(
                    {'error': 'You do not have permission to update this workflow step'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        new_status = request.data.get('status')
        if new_status:
            workflow_step.status = new_status
            
            if new_status == 'in_progress' and not workflow_step.started_at:
                workflow_step.started_at = timezone.now()
            
            if new_status == 'completed' and not workflow_step.completed_at:
                workflow_step.completed_at = timezone.now()
            
            workflow_step.save()
        
        serializer = WorkflowStepSerializer(workflow_step)
        return Response(serializer.data)
    
    except WorkflowStep.DoesNotExist:
        return Response(
            {'error': 'Workflow step not found'},
            status=status.HTTP_404_NOT_FOUND
        )


class WorkflowNotificationListView(generics.ListCreateAPIView):
    """
    List and create workflow notifications.
    """
    serializer_class = WorkflowNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get filtered queryset of notifications."""
        queryset = WorkflowNotification.objects.filter(user=self.request.user)
        
        # Filter by is_read
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        
        return queryset.select_related('user', 'workflow_step')


class WorkflowNotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a notification.
    """
    serializer_class = WorkflowNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get queryset of notifications."""
        return WorkflowNotification.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="Mark Notification as Read",
    description="Mark a notification as read.",
    responses={200: WorkflowNotificationSerializer}
)
def mark_notification_read(request, pk):
    """
    Mark a notification as read.
    """
    try:
        notification = WorkflowNotification.objects.get(pk=pk, user=request.user)
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        
        serializer = WorkflowNotificationSerializer(notification)
        return Response(serializer.data)
    
    except WorkflowNotification.DoesNotExist:
        return Response(
            {'error': 'Notification not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="Mark All Notifications as Read",
    description="Mark all notifications as read for the current user.",
    responses={200: 'All notifications marked as read'}
)
def mark_all_notifications_read(request):
    """
    Mark all notifications as read for the current user.
    """
    WorkflowNotification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True, read_at=timezone.now())
    
    return Response({'message': 'All notifications marked as read'})


class AuditLogListView(generics.ListAPIView):
    """
    List audit logs.
    """
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get filtered queryset of audit logs."""
        # Only HR and admin can view audit logs
        if self.request.user.role not in ['hr', 'admin']:
            return AuditLog.objects.none()
        
        queryset = AuditLog.objects.all()
        
        # Filter by user
        user_id = self.request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by action type
        action_type = self.request.query_params.get('action_type')
        if action_type:
            queryset = queryset.filter(action_type=action_type)
        
        # Filter by model name
        model_name = self.request.query_params.get('model_name')
        if model_name:
            queryset = queryset.filter(model_name=model_name)
        
        return queryset.select_related('user')


class AuditLogDetailView(generics.RetrieveAPIView):
    """
    Retrieve an audit log entry.
    """
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get queryset of audit logs."""
        # Only HR and admin can view audit logs
        if self.request.user.role not in ['hr', 'admin']:
            return AuditLog.objects.none()
        
        return AuditLog.objects.all()

