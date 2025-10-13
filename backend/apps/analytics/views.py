"""
Views for the analytics app.

This module contains API views for reports, dashboards, and metrics.
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db.models import Q, Count, Avg, F
from django.utils import timezone
from datetime import timedelta

from .models import Report, Dashboard, Metric
from .serializers import (
    ReportSerializer, ReportListSerializer,
    DashboardSerializer, DashboardListSerializer,
    MetricSerializer, MetricListSerializer
)
from apps.goals.models import Goal
from apps.reviews.models import Review
from apps.feedback.models import FeedbackRequest, FeedbackResponse
from apps.cycles.models import ReviewCycle
from apps.accounts.models import User


class ReportListView(generics.ListCreateAPIView):
    """
    Report list and creation endpoint.
    
    Provides list of reports with filtering,
    and allows creation of new reports.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method == 'GET':
            return ReportListSerializer
        return ReportSerializer
    
    def get_queryset(self):
        """Get filtered queryset of reports."""
        user = self.request.user
        queryset = Report.objects.select_related('created_by')
        
        # Filter by user's reports
        if not user.is_hr:
            queryset = queryset.filter(created_by=user)
        
        # Filter by report type
        report_type = self.request.query_params.get('type')
        if report_type:
            queryset = queryset.filter(report_type=report_type)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set created_by to current user when creating."""
        serializer.save(created_by=self.request.user)
    
    @extend_schema(
        summary="List Reports",
        description="Get a list of reports with optional filtering.",
        parameters=[
            OpenApiParameter(
                name='type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by report type'
            ),
            OpenApiParameter(
                name='status',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by status'
            ),
        ],
        responses={
            200: ReportListSerializer(many=True),
            401: "Authentication required"
        }
    )
    def get(self, request, *args, **kwargs):
        """Get list of reports."""
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create Report",
        description="Create a new report.",
        responses={
            201: ReportSerializer,
            400: "Validation error",
            401: "Authentication required"
        }
    )
    def post(self, request, *args, **kwargs):
        """Create a new report."""
        return super().post(request, *args, **kwargs)


class ReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Report detail endpoint.
    
    Provides detailed information about a specific report
    and allows updates and deletion.
    """
    
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'
    
    def get_queryset(self):
        """Get queryset filtered by user access."""
        user = self.request.user
        queryset = Report.objects.all()
        
        # Filter by user's reports unless HR
        if not user.is_hr:
            queryset = queryset.filter(created_by=user)
        
        return queryset
    
    @extend_schema(
        summary="Get Report Details",
        description="Retrieve detailed information about a specific report.",
        responses={
            200: ReportSerializer,
            404: "Report not found",
            401: "Authentication required"
        }
    )
    def get(self, request, *args, **kwargs):
        """Get report details."""
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update Report",
        description="Update a report's details.",
        responses={
            200: ReportSerializer,
            400: "Validation error",
            404: "Report not found",
            401: "Authentication required"
        }
    )
    def patch(self, request, *args, **kwargs):
        """Update report."""
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete Report",
        description="Delete a report.",
        responses={
            204: "Report deleted",
            404: "Report not found",
            401: "Authentication required"
        }
    )
    def delete(self, request, *args, **kwargs):
        """Delete report."""
        return super().delete(request, *args, **kwargs)


class DashboardListView(generics.ListCreateAPIView):
    """
    Dashboard list and creation endpoint.
    
    Provides list of dashboards with filtering,
    and allows creation of new dashboards.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method == 'GET':
            return DashboardListSerializer
        return DashboardSerializer
    
    def get_queryset(self):
        """Get filtered queryset of dashboards."""
        user = self.request.user
        queryset = Dashboard.objects.select_related('owner')
        
        # Show user's dashboards and public dashboards
        queryset = queryset.filter(
            Q(owner=user) | Q(is_public=True)
        )
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set owner to current user when creating."""
        serializer.save(owner=self.request.user)
    
    @extend_schema(
        summary="List Dashboards",
        description="Get a list of dashboards with optional filtering.",
        parameters=[
            OpenApiParameter(
                name='is_active',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter by active status'
            ),
        ],
        responses={
            200: DashboardListSerializer(many=True),
            401: "Authentication required"
        }
    )
    def get(self, request, *args, **kwargs):
        """Get list of dashboards."""
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create Dashboard",
        description="Create a new dashboard.",
        responses={
            201: DashboardSerializer,
            400: "Validation error",
            401: "Authentication required"
        }
    )
    def post(self, request, *args, **kwargs):
        """Create a new dashboard."""
        return super().post(request, *args, **kwargs)


class DashboardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Dashboard detail endpoint.
    
    Provides detailed information about a specific dashboard
    and allows updates and deletion.
    """
    
    serializer_class = DashboardSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'
    
    def get_queryset(self):
        """Get queryset filtered by user access."""
        user = self.request.user
        return Dashboard.objects.filter(
            Q(owner=user) | Q(is_public=True)
        )
    
    @extend_schema(
        summary="Get Dashboard Details",
        description="Retrieve detailed information about a specific dashboard.",
        responses={
            200: DashboardSerializer,
            404: "Dashboard not found",
            401: "Authentication required"
        }
    )
    def get(self, request, *args, **kwargs):
        """Get dashboard details."""
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update Dashboard",
        description="Update a dashboard's details.",
        responses={
            200: DashboardSerializer,
            400: "Validation error",
            404: "Dashboard not found",
            401: "Authentication required",
            403: "Permission denied"
        }
    )
    def patch(self, request, *args, **kwargs):
        """Update dashboard."""
        dashboard = self.get_object()
        if dashboard.owner != request.user:
            return Response(
                {'error': 'You can only update your own dashboards'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete Dashboard",
        description="Delete a dashboard.",
        responses={
            204: "Dashboard deleted",
            404: "Dashboard not found",
            401: "Authentication required",
            403: "Permission denied"
        }
    )
    def delete(self, request, *args, **kwargs):
        """Delete dashboard."""
        dashboard = self.get_object()
        if dashboard.owner != request.user:
            return Response(
                {'error': 'You can only delete your own dashboards'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().delete(request, *args, **kwargs)


class MetricListView(generics.ListCreateAPIView):
    """
    Metric list and creation endpoint.
    
    Provides list of metrics with filtering,
    and allows creation of new metrics (HR only).
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method == 'GET':
            return MetricListSerializer
        return MetricSerializer
    
    def get_queryset(self):
        """Get filtered queryset of metrics."""
        queryset = Metric.objects.all()
        
        # Filter by metric type
        metric_type = self.request.query_params.get('type')
        if metric_type:
            queryset = queryset.filter(metric_type=metric_type)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('name')
    
    @extend_schema(
        summary="List Metrics",
        description="Get a list of metrics with optional filtering.",
        parameters=[
            OpenApiParameter(
                name='type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by metric type'
            ),
            OpenApiParameter(
                name='is_active',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter by active status'
            ),
        ],
        responses={
            200: MetricListSerializer(many=True),
            401: "Authentication required"
        }
    )
    def get(self, request, *args, **kwargs):
        """Get list of metrics."""
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create Metric",
        description="Create a new metric (HR only).",
        responses={
            201: MetricSerializer,
            400: "Validation error",
            401: "Authentication required",
            403: "Permission denied"
        }
    )
    def post(self, request, *args, **kwargs):
        """Create a new metric."""
        # Check if user is HR or admin
        if not request.user.is_hr:
            return Response(
                {'error': 'Only HR can create metrics'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().post(request, *args, **kwargs)


class MetricDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Metric detail endpoint.
    
    Provides detailed information about a specific metric
    and allows updates (HR only).
    """
    
    serializer_class = MetricSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Metric.objects.all()
    lookup_field = 'pk'
    
    @extend_schema(
        summary="Get Metric Details",
        description="Retrieve detailed information about a specific metric.",
        responses={
            200: MetricSerializer,
            404: "Metric not found",
            401: "Authentication required"
        }
    )
    def get(self, request, *args, **kwargs):
        """Get metric details."""
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update Metric",
        description="Update a metric (HR only).",
        responses={
            200: MetricSerializer,
            400: "Validation error",
            404: "Metric not found",
            401: "Authentication required",
            403: "Permission denied"
        }
    )
    def patch(self, request, *args, **kwargs):
        """Update metric."""
        if not request.user.is_hr:
            return Response(
                {'error': 'Only HR can update metrics'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete Metric",
        description="Delete a metric (HR only).",
        responses={
            204: "Metric deleted",
            404: "Metric not found",
            401: "Authentication required",
            403: "Permission denied"
        }
    )
    def delete(self, request, *args, **kwargs):
        """Delete metric."""
        if not request.user.is_hr:
            return Response(
                {'error': 'Only HR can delete metrics'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().delete(request, *args, **kwargs)


# Dashboard Statistics Endpoints

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="Get Dashboard Statistics",
    description="Get general dashboard statistics for the current user.",
    responses={200: "Dashboard statistics"}
)
def dashboard_stats(request):
    """Get general dashboard statistics."""
    user = request.user
    
    # Get active goals count
    active_goals = Goal.objects.filter(employee=user, status='in_progress').count()
    
    # Get pending reviews count
    pending_reviews = Review.objects.filter(
        Q(employee=user, status__in=['pending', 'in_progress']) |
        Q(reviewer=user, status__in=['pending', 'in_progress'])
    ).count()
    
    # Get feedback received count
    feedback_received = FeedbackRequest.objects.filter(recipient=user).count()
    
    # Calculate completion rate
    total_goals = Goal.objects.filter(employee=user).count()
    completed_goals = Goal.objects.filter(employee=user, status='completed').count()
    completion_rate = (completed_goals / total_goals * 100) if total_goals > 0 else 0
    
    return Response({
        'active_goals': active_goals,
        'pending_reviews': pending_reviews,
        'feedback_received': feedback_received,
        'completion_rate': round(completion_rate, 1)
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="Get Employee Dashboard Statistics",
    description="Get detailed statistics for employee dashboard.",
    responses={200: "Employee dashboard statistics"}
)
def employee_dashboard_stats(request):
    """Get employee dashboard statistics."""
    user = request.user
    
    # Get goals
    goals = Goal.objects.filter(employee=user).order_by('-created_at')[:5]
    goals_data = [{
        'id': g.id,
        'title': g.title,
        'progress_percentage': g.progress_percentage,
        'status': g.status,
        'target_date': g.target_date.isoformat() if g.target_date else None
    } for g in goals]
    
    # Get current review cycle
    current_cycle = ReviewCycle.objects.filter(
        status='active',
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    ).first()
    
    cycle_data = None
    if current_cycle:
        # Calculate user's completion percentage for this cycle
        total_tasks = 5  # Example: goals submission, self-review, feedback, etc.
        completed_tasks = 0
        
        if Goal.objects.filter(employee=user, created_at__gte=current_cycle.start_date).exists():
            completed_tasks += 1
        if Review.objects.filter(employee=user, cycle=current_cycle, review_type='self_review', status='completed').exists():
            completed_tasks += 1
            
        completion = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        cycle_data = {
            'id': current_cycle.id,
            'name': current_cycle.name,
            'description': current_cycle.description,
            'completion_percentage': round(completion, 1),
            'start_date': current_cycle.start_date.isoformat(),
            'end_date': current_cycle.end_date.isoformat()
        }
    
    return Response({
        'recent_goals': goals_data,
        'current_cycle': cycle_data,
        'stats': {
            'total_goals': Goal.objects.filter(employee=user).count(),
            'completed_goals': Goal.objects.filter(employee=user, status='completed').count(),
            'feedback_count': FeedbackRequest.objects.filter(recipient=user).count()
        }
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="Get Manager Dashboard Statistics",
    description="Get detailed statistics for manager dashboard.",
    responses={200: "Manager dashboard statistics"}
)
def manager_dashboard_stats(request):
    """Get manager dashboard statistics."""
    user = request.user
    
    # Get team members (employees reporting to this manager)
    team_members = User.objects.filter(manager=user, status='active')
    total_members = team_members.count()
    
    # Get team goals statistics
    team_goals = Goal.objects.filter(employee__in=team_members)
    total_goals = team_goals.count()
    completed_goals = team_goals.filter(status='completed').count()
    
    # Get pending reviews for team
    pending_reviews = Review.objects.filter(
        employee__in=team_members,
        reviewer=user,
        status__in=['pending', 'in_progress']
    ).select_related('employee', 'cycle')[:10]
    
    reviews_data = [{
        'id': r.id,
        'employee_name': r.employee.full_name,
        'employee_id': r.employee.id,
        'review_type': r.review_type,
        'status': r.status,
        'cycle': r.cycle.name if r.cycle else None
    } for r in pending_reviews]
    
    # Calculate average team rating
    completed_reviews = Review.objects.filter(
        employee__in=team_members,
        reviewer=user,
        status='completed',
        overall_rating__isnull=False
    )
    avg_rating = completed_reviews.aggregate(Avg('overall_rating'))['overall_rating__avg'] or 0
    
    return Response({
        'team_stats': {
            'total_members': total_members,
            'total_goals': total_goals,
            'goals_completed': completed_goals,
            'average_rating': round(avg_rating, 1)
        },
        'pending_reviews': reviews_data,
        'team_members': [{
            'id': m.id,
            'full_name': m.full_name,
            'email': m.email,
            'position': m.job_title
        } for m in team_members[:10]]
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="Get HR Dashboard Statistics",
    description="Get detailed statistics for HR/Admin dashboard.",
    responses={200: "HR dashboard statistics"}
)
def hr_dashboard_stats(request):
    """Get HR dashboard statistics."""
    # Total employees
    total_employees = User.objects.filter(status='active').count()
    
    # Active review cycles
    active_cycles = ReviewCycle.objects.filter(status='active').count()
    
    # Completed reviews
    completed_reviews = Review.objects.filter(status='completed').count()
    
    # Pending feedback/actions
    pending_feedback = FeedbackRequest.objects.filter(status='pending').count()
    
    # Department performance
    from apps.org.models import Department
    departments = Department.objects.filter(is_active=True).annotate(
        employee_count=Count('employees', filter=Q(employees__status='active'))
    )[:10]
    
    dept_data = []
    for dept in departments:
        # Calculate department performance score
        dept_employees = User.objects.filter(department=dept, status='active')
        dept_goals = Goal.objects.filter(employee__in=dept_employees)
        completed = dept_goals.filter(status='completed').count()
        total = dept_goals.count()
        
        dept_reviews = Review.objects.filter(
            employee__in=dept_employees,
            status='completed',
            overall_rating__isnull=False
        )
        avg_rating = dept_reviews.aggregate(Avg('overall_rating'))['overall_rating__avg'] or 0
        
        dept_data.append({
            'name': dept.name,
            'employee_count': dept.employee_count,
            'performance_score': round(avg_rating * 20, 1),  # Convert to 100-point scale
            'goal_completion': round((completed / total * 100) if total > 0 else 0, 1),
            'avg_rating': round(avg_rating, 1)
        })
    
    # Recent activity
    recent_reviews = Review.objects.filter(
        status='completed'
    ).order_by('-submitted_at').select_related('employee')[:5]
    
    recent_goals = Goal.objects.filter(
        status='submitted'
    ).order_by('-created_at').select_related('employee')[:5]
    
    activity_data = []
    
    for review in recent_reviews:
        activity_data.append({
            'id': review.id,
            'type': 'review',
            'description': f"{review.employee.full_name} completed {review.review_type.replace('_', ' ')}",
            'timestamp': review.submitted_at.isoformat() if review.submitted_at else None,
            'color': 'green'
        })
    
    for goal in recent_goals:
        activity_data.append({
            'id': goal.id,
            'type': 'goal',
            'description': f"{goal.employee.full_name} submitted new goal",
            'timestamp': goal.created_at.isoformat(),
            'color': 'blue'
        })
    
    # Sort by timestamp
    activity_data.sort(key=lambda x: x['timestamp'] if x['timestamp'] else '', reverse=True)
    activity_data = activity_data[:10]
    
    # Alerts
    alerts_data = []
    
    # Check for ending review cycles
    ending_soon = ReviewCycle.objects.filter(
        status='active',
        end_date__lte=timezone.now() + timedelta(days=7),
        end_date__gte=timezone.now()
    )
    for cycle in ending_soon:
        days_left = (cycle.end_date - timezone.now().date()).days
        alerts_data.append({
            'id': cycle.id,
            'title': 'Review Cycle Ending',
            'message': f"{cycle.name} ends in {days_left} days",
            'icon': 'mdi-clock-alert',
            'color': 'orange'
        })
    
    # Check for pending goal approvals
    pending_goal_approvals = Goal.objects.filter(status='submitted').count()
    if pending_goal_approvals > 0:
        alerts_data.append({
            'id': 'goals',
            'title': 'Goal Approval Needed',
            'message': f"{pending_goal_approvals} goals pending approval",
            'icon': 'mdi-target',
            'color': 'blue'
        })
    
    # Check for low performance
    low_performers = Review.objects.filter(
        status='completed',
        overall_rating__lt=2.5,
        submitted_at__gte=timezone.now() - timedelta(days=90)
    ).values('employee').distinct().count()
    
    if low_performers > 0:
        alerts_data.append({
            'id': 'performance',
            'title': 'Performance Alert',
            'message': f"{low_performers} employees below target",
            'icon': 'mdi-alert',
            'color': 'red'
        })
    
    return Response({
        'stats': {
            'total_employees': total_employees,
            'active_cycles': active_cycles,
            'completed_reviews': completed_reviews,
            'pending_feedback': pending_feedback
        },
        'department_performance': dept_data,
        'recent_activity': activity_data,
        'alerts': alerts_data
    })

