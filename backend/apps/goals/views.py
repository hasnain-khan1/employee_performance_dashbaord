"""
Views for the goals app.

This module contains API views for goal management,
including SMART goal creation, tracking, and evaluation.
"""

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db.models import Q

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