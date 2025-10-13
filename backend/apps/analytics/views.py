"""
Views for the analytics app.

This module contains API views for reports, dashboards, and metrics.
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db.models import Q

from .models import Report, Dashboard, Metric
from .serializers import (
    ReportSerializer, ReportListSerializer,
    DashboardSerializer, DashboardListSerializer,
    MetricSerializer, MetricListSerializer
)


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

